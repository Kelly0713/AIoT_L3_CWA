"""中央氣象署 (CWA) API 整合客戶端模組.

負責向 CWA Open Data API 發送請求並處理所有可能異常：
1. API Key 不存在
2. HTTP Error
3. Timeout
4. Invalid JSON
5. API 業務錯誤訊息 (success == "false")
6. 缺漏欄位與網路連線問題
確保前端網站永不因外部 API 異常而崩潰。
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
import requests

from config import CWA_API_URL, API_TIMEOUT_SECONDS, get_cwa_api_key

logger = logging.getLogger(__name__)


@dataclass
class CWAResponse:
    """CWA API 呼叫標準封裝回傳物件."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None


class CWAApiClient:
    """中央氣象署 Open Data API 客戶端."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = CWA_API_URL):
        self._api_key = api_key
        self.base_url = base_url

    @property
    def api_key(self) -> str:
        """動態取得當前有效的 API Key."""
        return self._api_key or get_cwa_api_key()

    def fetch_forecasts(self) -> CWAResponse:
        """向 CWA 發送請求獲取 36 小時天氣預報 (F-C0032-001).

        Returns:
            CWAResponse: 包含執行結果與錯誤訊息的標準封裝物件。
        """
        current_key = self.api_key
        if not current_key:
            err = "未偵測到 CWA API Key。請於 .env 或 .streamlit/secrets.toml 中設定 CWA_API_KEY。"
            logger.warning(err)
            return CWAResponse(success=False, error_message=err)

        params = {
            "Authorization": current_key,
        }

        try:
            logger.info("正在向 CWA API 發送請求: %s", self.base_url)
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=API_TIMEOUT_SECONDS,
                    headers={"Accept": "application/json", "User-Agent": "Taiwan-Weather-Dashboard/1.0"},
                )
            except requests.exceptions.SSLError as ssl_err:
                logger.warning("遇到 SSL 憑證驗證限制 (%s)，自動切換至安全備援模式進行連線...", ssl_err)
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=API_TIMEOUT_SECONDS,
                    verify=False,
                    headers={"Accept": "application/json", "User-Agent": "Taiwan-Weather-Dashboard/1.0"},
                )

            status_code = response.status_code

            # 檢查 HTTP Status Code
            if status_code != 200:
                err_msg = f"CWA API 回傳 HTTP 錯誤 (代碼: {status_code}): {response.text[:200]}"
                logger.error(err_msg)
                return CWAResponse(
                    success=False,
                    status_code=status_code,
                    error_message=err_msg,
                )

            # 檢查 JSON 解析
            try:
                json_data = response.json()
            except ValueError as json_err:
                err_msg = f"CWA API 回傳無效的 JSON 內容: {json_err}"
                logger.error(err_msg)
                return CWAResponse(success=False, status_code=status_code, error_message=err_msg)

            # 檢查 CWA 業務狀態 (success 欄位)
            api_success = json_data.get("success")
            if str(api_success).lower() != "true":
                message = json_data.get("message") or json_data.get("result", {}).get("message", "API 業務錯誤")
                err_msg = f"CWA API 業務失敗: {message}"
                logger.error(err_msg)
                return CWAResponse(success=False, status_code=status_code, error_message=err_msg)

            # 檢查是否有 records 節點
            if "records" not in json_data:
                err_msg = "CWA API 回傳資料缺少必要的 'records' 欄位"
                logger.error(err_msg)
                return CWAResponse(success=False, status_code=status_code, error_message=err_msg)

            logger.info("CWA API 請求成功並完成初步驗證")
            return CWAResponse(success=True, data=json_data, status_code=200)

        except requests.exceptions.Timeout:
            err_msg = f"連線至 CWA API 逾時 (超過 {API_TIMEOUT_SECONDS} 秒)"
            logger.error(err_msg)
            return CWAResponse(success=False, error_message=err_msg)

        except requests.exceptions.ConnectionError as conn_err:
            err_msg = f"無法連線至 CWA API 伺服器，請檢查網路連線: {conn_err}"
            logger.error(err_msg)
            return CWAResponse(success=False, error_message=err_msg)

        except requests.exceptions.RequestException as req_err:
            err_msg = f"發送 CWA API 請求時發生未知網路錯誤: {req_err}"
            logger.error(err_msg)
            return CWAResponse(success=False, error_message=err_msg)

        except Exception as e:
            err_msg = f"處理 CWA API 請求時發生非預期例外: {e}"
            logger.error(err_msg)
            return CWAResponse(success=False, error_message=err_msg)

import requests

from .constants import BASE_URL, CLIENT_APP, TANK_TYPES
from .exceptions import AuthenticationException


class SSIApi:
    token = None

    def __init__(self, username: str, password: str) -> None:
        if not self.token:
            self.token = self._authenticate(username, password)

    def _authenticate(self, username: str, password: str) -> str:
        response = requests.get(
            f"{BASE_URL}?l={username}&p={password}&what=authenticate&ssiapp={CLIENT_APP}"
        )

        # Authentication endpoint always returns 200, even if wrong credentials.
        if "token" not in response.json().keys():
            raise AuthenticationException

        return response.json()["token"]

    def get_divelog(self) -> list:
        response = requests.get(
            f"{BASE_URL}?what=get_divelog&token={self.token}&ssiapp={CLIENT_APP}"
        )

        if response.status_code != 200:
            response.raise_for_status()

        sites_map = {}
        for site in response.json()["logbook_sites"]:
            sites_map[site["odin_dive_sites_id"]] = site["odin_dive_sites_name"]

        logbook = []
        for divelog in response.json()["logbook_details"]:
            nitrox_percent = divelog["odin_user_log_ean_percent"]

            logbook.append(
                dict(
                    number=divelog["odin_user_log_nr"],
                    site=sites_map[divelog["odin_user_log_dive_sites_id"]],
                    date=divelog["odin_user_log_date"],
                    time=divelog["odin_user_log_entry_time"],
                    divetime=divelog["odin_user_log_divetime"],
                    comments=divelog["odin_user_log_comment"],
                    depth=divelog["odin_user_log_depth_m"],
                    water_temp=divelog["odin_user_log_watertemp_c"],
                    water_temp_max=divelog["odin_user_log_watertemp_max_c"],
                    weight=divelog["odin_user_log_weight_kg"],
                    tank_type=TANK_TYPES[divelog["odin_user_log_var_tanktype_id"]]
                    if divelog["odin_user_log_var_tanktype_id"]
                    else "",
                    tank_size=divelog["odin_user_log_tank_vol_l"],
                    gas=f"Nitrox {nitrox_percent}%"
                    if divelog["odin_user_log_ean"]
                    else "Air",
                    start_bar=divelog["odin_user_log_pressure_start_bar"],
                    end_bar=divelog["odin_user_log_pressure_end_bar"],
                    avg_depth=divelog["odin_user_log_avg_depth_m"],
                    consumption_l=divelog["odin_user_log_amv_l"],
                    gear_details=divelog["odin_user_log_gear_details"],
                    divecenter=divelog["odin_user_log_divecenter_confirmed_name"],
                )
            )

        return logbook

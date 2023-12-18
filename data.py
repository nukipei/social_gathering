import pandas as pd
import numpy as np
import os
import json


class EmployeeData:
    employee_col_name = "社員番号"
    team_col_name = "所属チーム"
    age_col_name = "年齢層"

    def __init__(self, num_employees=100, num_teams=7, p=0.4):
        # データの生成
        self.num_employees = num_employees  # 生成する社員数
        self.num_teams = num_teams  # チーム数
        self.p = p  # 若手の割合

        self.EMPLOYEES_DEGIT = 3  # 社員番号の桁数

        self.idx2employees_number = [
            f"{i:0{self.EMPLOYEES_DEGIT}}" for i in range(1, num_employees + 1)
        ]
        self.idx2teams_name = [chr(ord("A") + i) for i in range(num_teams)]  # 所属チーム
        self.idx2age_name = ["若手", "ベテラン"]  # 年齢層

        self.employees_number2idx = {
            v: k for k, v in enumerate(self.idx2employees_number)
        }
        self.teams_name2idx = {v: k for k, v in enumerate(self.idx2teams_name)}
        self.age_name2idx = {v: k for k, v in enumerate(self.idx2age_name)}

        self.data_path = f"employee_data_{self.num_teams}_{self.num_employees}_{self.p}"

    def generate_data_csv(self, s=0):
        np.random.seed(s)

        data = {
            self.employee_col_name: self.idx2employees_number,
            self.team_col_name: np.random.choice(
                self.idx2teams_name, self.num_employees
            ),
            self.age_col_name: np.random.choice(
                self.idx2age_name, self.num_employees, p=[self.p, 1 - self.p]
            ),
        }

        df = pd.DataFrame(data)

        # CSVファイルとして出力
        if not os.path.exists("data"):
            os.mkdir("data")
        df.to_csv(
            f"data/input/{self.data_path}_{s}.csv",
            index=False,
        )

        # 生成したデータフレームの表示
        print(df)

    def generate_data_json(self, s=0):
        np.random.seed(s)

        data = {
            self.employee_col_name: self.idx2employees_number,
            self.team_col_name: np.random.choice(
                self.idx2teams_name, self.num_employees
            ).tolist(),
            self.age_col_name: np.random.choice(
                self.idx2age_name, self.num_employees, p=[self.p, 1 - self.p]
            ).tolist(),
        }

        # df = pd.DataFrame(data)
        output = {
            "num_employee": self.num_employees,
            "num_teams": self.num_teams,
            "p": self.p,
            "seed": s,
            "data": data,
        }

        # JSONファイルとして出力
        if not os.path.exists("data"):
            os.mkdir("data")
        with open(
            f"data/{self.data_path}_{s}.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(output, f, ensure_ascii=False)
        # df.to_json(f'data/employee_data_{self.num_teams}_{self.num_employees}_{self.p}_{s}.json', orient='records',force_ascii=False)

        # 生成したデータフレームの表示
        print(output)


if __name__ == "__main__":
    employee_data = EmployeeData(num_employees=100, num_teams=3, p=0.4)
    employee_data.generate_data_csv(s=1)

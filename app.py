import os
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from data import EmployeeData
from social_gathering import solve_social_gathering


def main():
    emp = EmployeeData(num_employees=1, num_teams=1)

    # セッションステートの初期化
    if "data_upload" not in st.session_state:
        # データがアップロードされたかどうか
        st.session_state.data_upload: bool = False
    if "df" not in st.session_state:
        # データがアップロードされたかどうか
        st.session_state.df: Optional[pd.DataFrame] = None
    if "num_people" not in st.session_state:
        # データがアップロードされたかどうか
        st.session_state.num_people: Optional[int] = None
    if "solved" not in st.session_state:
        # 求解が終了したかどうか
        st.session_state.solved: bool = False
    if "result_employee_idx" not in st.session_state:
        # グループごとの社員のindexリスト
        st.session_state.result_employee_idx: List[int] = list()
    if "result_age_idx" not in st.session_state:
        # グループごとの年齢層のリスト
        st.session_state.result_age_idx: List[int] = list()
    if "result_team_idx" not in st.session_state:
        # グループごとのチームのリスト
        st.session_state.result_team_idx: List[int] = list()
    if "group_employee_list" not in st.session_state:
        # グループ名ごとの社員番号のリストを示した辞書（画面表示用）
        st.session_state.group_employee_list: Dict[str, str] = dict()

    # 画面全体の設定
    st.set_page_config(
        page_title="グループ分けアプリ",
        page_icon="🧊",
        layout="centered",
        # initial_sidebar_state="collapsed",
    )

    # サイドバーの設定
    # タイトルを設定
    st.markdown(
        """
        # グループ分けアプリ

        + ##### 社員のデータを読み込み、グループ分けを行うアプリです。
          + 詳細は https://qiita.com/nukipei/items/ee14f83a436231d3a0e5 参照
        + ##### まずは、左のサイドバーからインプットデータを設定してください。
        + ##### 設定が完了したら、下の「グループ分け実行」ボタンを押してください。
        """
    )

    # インプットデータの設定
    st.sidebar.markdown(
        """
        ## 最適化条件の設定
        """
    )

    # 社員数を設定
    st.sidebar.markdown(
        """
        ### 1. 入力データを設定
        各社員の社員番号,所属チーム,年齢層（ベテランor若手）をCSV形式で指定しアップロードする \\
        詳細はサンプルデータを参照
        """
    )
    st.sidebar.download_button(
        "サンプルデータのダウンロード",
        open(os.path.join("data\input\sample_input.csv"), "br"),
        "sample_input.csv",
    )

    csv_file = st.sidebar.file_uploader("入力データのアップロード", type=["csv"])
    df = None
    num_employees = None
    num_teams = None
    if csv_file is not None:
        df = pd.read_csv(csv_file)

        num_employees = len(df)
        num_teams = len(df[EmployeeData.team_col_name].drop_duplicates())

        st.sidebar.markdown(
            f"""
            社員数: {num_employees}
            チーム数: {num_teams}
            """
        )

        emp = EmployeeData(num_employees=num_employees, num_teams=num_teams)

        with st.sidebar.expander("データを表示"):
            st.dataframe(df, hide_index=True)

        st.session_state.data_upload = True

    # 1グループの人数を設定
    st.sidebar.markdown(
        """
        ### 2. 1グループの人数を設定
        1グループの人数（割り切れないときは一部グループが+1人）を設定する
        """
    )

    num_people = st.sidebar.number_input(
        "1グループの人数", min_value=1, max_value=num_employees or 1000000, value=7
    )

    # データの前準備
    age_list = []  # 年齢層のリスト
    team_list = []  # チームのリスト
    num_group = 0  # グループ数
    group_name_list = []  # グループ名のリスト

    # グループ分け実行
    if st.button("グループ分け実行"):
        if st.session_state.data_upload is False:
            st.error(
                "入力データが指定されていません。サイドバーから入力データを指定してください。"
            )
        else:
            age_list = [
                emp.age_name2idx[age] for age in df[EmployeeData.age_col_name]
            ]  # 年齢層のリスト
            team_list = [
                emp.teams_name2idx[team] for team in df[EmployeeData.team_col_name]
            ]  # チームのリスト
            num_group = num_employees // num_people  # グループ数
            group_name_list = [
                f"グループ_{group_idx:02}" for group_idx in range(num_group)
            ]  # グループ名のリスト

            st.session_state.df = df
            st.session_state.num_people = num_people
            with st.spinner("計算中"):
                # groupごとの社員のindex、年齢、チームのリストを返す
                (
                    st.session_state.result_employee_idx,
                    st.session_state.result_age_idx,
                    st.session_state.result_team_idx,
                ) = solve_social_gathering(
                    num_employees, num_group, team_list, age_list
                )

                # グループ名ごとの社員番号のリストを返す
                for group_idx in range(num_group):
                    st.session_state.group_employee_list[group_name_list[group_idx]] = {
                        i: emp.idx2employees_number[
                            st.session_state.result_employee_idx[group_idx][i]
                        ]
                        for i in range(
                            len(st.session_state.result_employee_idx[group_idx])
                        )
                    }
            st.session_state.solved = True

    if id(df) != id(st.session_state.df):
        st.session_state.data_upload = False
        st.session_state.solved = False
    if num_people != st.session_state.num_people:
        st.session_state.solved = False

    if st.session_state.solved:
        # 20のカラーリスト
        COLOR_LIST = [
            "#AED6F1",
            "#F8C471",
            "#73C6B6",
            "#FAD02E",
            "#D2B4DE",
            "#F5B7B1",
            "#82E0AA",
            "#F0B27A",
            "#ABEBC6",
            "#85C1E9",
        ]

        def apply_txt_age(x):
            if (
                len(x) == emp.EMPLOYEES_DEGIT
                and age_list[emp.employees_number2idx[x[0 : emp.EMPLOYEES_DEGIT]]] == 0
            ):
                return x + "★"
            else:
                return x + "　"

        def apply_txt_team(x):
            return x + "　"

        def apply_style_team(x):
            if len(x) < emp.EMPLOYEES_DEGIT:
                return "background-color: #FFFFFF"
            idx = emp.employees_number2idx[x[0 : emp.EMPLOYEES_DEGIT]]
            return f"background-color: {COLOR_LIST[team_list[idx] % len(COLOR_LIST)]}"

        def apply_style_age(x):
            if len(x) < emp.EMPLOYEES_DEGIT:
                return "background-color: #FFFFFF"

            idx = emp.employees_number2idx[x[0 : emp.EMPLOYEES_DEGIT]]

            return f"background-color: {COLOR_LIST[age_list[idx] % len(COLOR_LIST)]}"

        # 結果の表示
        st.markdown(
            """
            ## 結果
            """
        )

        # グループごとの社員一覧をDataFrameに変換
        # さらに、nanを空文字に変換
        output = pd.DataFrame(st.session_state.group_employee_list).T.fillna("")

        # グループごとの社員一覧を表示
        st.markdown(
            """
            ### グループごとの社員一覧
            各表の値は社員番号であり、末尾が★の社員は若手であることを示す。
            """
        )
        tab1, tab2, tab3 = st.tabs(["デフォルト", "年齢層", "チーム"])
        # tab1: デフォルト
        tab1.table(output.applymap(apply_txt_age))
        # tab2: 年齢層が若手の人に、末尾に★を付加し表示
        tab2.table(output.applymap(apply_txt_age).style.applymap(apply_style_age))
        # tab3: チームごとに色をつけて表示
        tab3.table(output.applymap(apply_txt_age).style.applymap(apply_style_team))

        st.markdown(
            """
            ### グループごとの年齢層、チームの内訳

            グループごとの年齢層、チームの内訳を表示する。
            """
        )
        tab1, tab2 = st.tabs(["年齢層", "チーム"])
        # 年齢層の内訳を表示
        group_young_count = list()
        group_old_count = list()
        for group_idx in range(num_group):
            group_young_count.append(
                st.session_state.result_age_idx[group_idx].count(0)
            )
            group_old_count.append(st.session_state.result_age_idx[group_idx].count(1))

        chart_data = pd.DataFrame(
            {
                "グループ名": group_name_list,
                emp.idx2age_name[0]: group_young_count,
                emp.idx2age_name[1]: group_old_count,
            }
        )
        tab1.bar_chart(
            chart_data,
            x="グループ名",
            y=emp.idx2age_name,
            color=COLOR_LIST[: len(emp.idx2age_name)],
        )

        # チームの内訳を表示
        group_team_list = {k: list() for k in emp.idx2teams_name}
        for group_idx in range(num_group):
            for k in group_team_list.keys():
                group_team_list[k].append(
                    st.session_state.result_team_idx[group_idx].count(
                        emp.teams_name2idx[k]
                    )
                )
        group_team_list["グループ名"] = group_name_list
        chart_data = pd.DataFrame(group_team_list)
        tab2.bar_chart(
            chart_data,
            x="グループ名",
            y=emp.idx2teams_name,
            color=COLOR_LIST[: len(emp.idx2teams_name)],
        )

        # チーム被り状況を表示
        # チームごとの最大被り数を計算
        max_team_overlap_count = [
            max(
                [
                    st.session_state.result_team_idx[group_idx].count(team_idx)
                    for group_idx in range(num_group)
                ]
            )
            for team_idx in range(num_teams)
        ]

        # チームごとの若手同士の被り数を計算
        max_team_young_overlap_count = [
            max(
                [
                    [
                        t_id
                        for idx, t_id in enumerate(
                            st.session_state.result_team_idx[group_idx]
                        )
                        if age_list[
                            st.session_state.result_employee_idx[group_idx][idx]
                        ]
                        == 0
                    ].count(team_idx)
                    for group_idx in range(num_group)
                ]
            )
            for team_idx in range(num_teams)
        ]

        # チームごとのベテラン同士の被り数を計算
        max_team_old_overlap_count = [
            max(
                [
                    [
                        t_id
                        for idx, t_id in enumerate(
                            st.session_state.result_team_idx[group_idx]
                        )
                        if age_list[
                            st.session_state.result_employee_idx[group_idx][idx]
                        ]
                        == 1
                    ].count(team_idx)
                    for group_idx in range(num_group)
                ]
            )
            for team_idx in range(num_teams)
        ]

        # st.markdown(
        #     """
        #     ### チーム被り状況（全体）

        #     以下について、各グループ、各チームで最も大きい値を表示する。
        #     + 若手・ベテラン全員でのチーム被り数
        #     + 若手同士のチーム被り数
        #     + ベテラン同士のチーム被り数
        #     """
        # )
        # col1, col2, col3 = st.columns(3)
        # col1.metric("チーム被り数", max(max_team_overlap_count))
        # col2.metric("若手同士の被り数", max(max_team_young_overlap_count))
        # col3.metric("ベテラン同士の被り数", max(max_team_old_overlap_count))

        # チーム被り状況を表示
        st.markdown(
            """
            ### チーム被り状況

            以下について、各グループで最も大きい値をチームごとに表示する。
            + 若手・ベテラン全員でのチーム被り数
            + 若手同士のチーム被り数
            + ベテラン同士のチーム被り数
            """
        )
        # チームインデックスをスクロールバーで選択
        selected_team_name = st.selectbox("チーム名を選択", emp.idx2teams_name)

        col1, col2 = st.columns(2)
        col1.metric(
            "若手同士の被り数",
            max_team_young_overlap_count[emp.teams_name2idx[selected_team_name]],
        )
        col2.metric(
            "ベテラン同士の被り数",
            max_team_old_overlap_count[emp.teams_name2idx[selected_team_name]],
        )

        # 該当のチームのみを色をつけて表示
        st.table(
            output.applymap(apply_txt_age).style.applymap(
                lambda x: "background-color: #FFFFFF"
                if len(x) < emp.EMPLOYEES_DEGIT
                or emp.teams_name2idx[selected_team_name]
                != team_list[emp.employees_number2idx[x[0 : emp.EMPLOYEES_DEGIT]]]
                else apply_style_team(x)
            )
        )

        # csvファイルを出力
        st.markdown(
            """
            ### CSVファイルの出力

            グループごとの社員番号をCSVファイルとして出力する。
            """
        )
        # csv用のdfを用意＆グループ名を追加
        output_csv = output.copy()
        output_csv["グループ名"] = group_name_list
        # csvファイルをdata/outputに出力
        output_csv.set_index("グループ名").to_csv(
            f"data//output/output_employee{num_employees}_team{num_teams}.csv",
            header=False,
            encoding="utf_8_sig",
        )
        # csvファイルをダウンロード
        with open(
            f"data/output/output_employee{num_employees}_team{num_teams}.csv", "rb"
        ) as f:
            st.download_button(
                label="CSVファイルをダウンロード",
                data=f,
                file_name=f"output_employee{num_employees}_team{num_teams}.csv",
            )


if __name__ == "__main__":
    main()

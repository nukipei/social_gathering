import pulp
import numpy as np


class SocialGathering:
    def __init__(self, N: int, G: int, team_list: list, age_list: list) -> None:
        """
        N: 人数
        G: グループ数
        team_list: 各社員の所属チーム
        age_list: 各社員の年齢層(0: 若手, 1: ベテラン）
        """

        self.N = N
        self.team_list = team_list
        self.G = G
        self.age_list = age_list

        # T: チーム数
        self.T = len(self.team_list)

        # group_n_list: 各グループの人数
        n_by_grp = self.N // self.G  # 1グループの人数(割り切れないときは一部グループが+1人)
        pls_1_grp = self.N % self.G  # +1人のグループの数
        self.group_n_list = [n_by_grp + 1] * pls_1_grp + [n_by_grp] * (
            self.G - pls_1_grp
        )

        # young_n_list: グループごとの若手の人数
        yng_n_by_grp = len([a for a in self.age_list if a == 0]) // self.G
        yng_plus_1_grp = len([a for a in age_list if a == 0]) % G
        self.young_n_list = np.array(
            [yng_n_by_grp + 1] * yng_plus_1_grp + [yng_n_by_grp] * (G - yng_plus_1_grp)
        )

        # x： nがグループgに入るとき1, そうでないとき0を示す変数
        # g: グループの番号, n: 人の番号
        self.x = [
            [
                pulp.LpVariable("x_{}_{}".format(n, g), cat="Binary")
                for g in range(self.G)
            ]
            for n in range(self.N)
        ]

        # 各グループのチーム被り数の最大値と最小値を示す変数
        self.max_overlap = pulp.LpVariable(f"max_overlap", lowBound=0, upBound=8)
        self.min_overlap = pulp.LpVariable(f"min_overlap", lowBound=0, upBound=8)

        # 各グループの若手のチーム被り数の最大値と最小値を示す変数
        self.max_young_overlap = pulp.LpVariable(
            f"max_young_overlap", lowBound=0, upBound=8
        )
        self.min_young_overlap = pulp.LpVariable(
            f"min_young_overlap", lowBound=0, upBound=8
        )

        # 各若手と同じグループのベテランのチーム被り数の最大値と最小値を示す変数
        self.max_young_overlap_with_old = pulp.LpVariable(
            f"max_young_overlap_with_old", lowBound=0, upBound=8
        )
        self.min_young_overlap_with_old = pulp.LpVariable(
            f"min_young_overlap_with_old ", lowBound=0, upBound=8
        )

        # 各グループのベテランのチーム被り数の最大値と最小値を示す変数
        self.max_old_overlap = pulp.LpVariable(
            f"max_old_overlap", lowBound=0, upBound=8
        )
        self.min_old_overlap = pulp.LpVariable(
            f"min_old_overlap", lowBound=0, upBound=8
        )

        # グループgに、チームtの若手が存在するとき1, そうでないとき0を示す変数
        # g: グループの番号, t: チームの番号
        self.y = [
            [
                pulp.LpVariable("y_{}_{}".format(g, t), cat="Binary")
                for t in range(self.T)
            ]
            for g in range(self.G)
        ]

        self.prob = pulp.LpProblem("social_gathering")

    def set_objective(self, ob):
        self.prob += ob

    def set_only_one_group(self):
        # 各人は一つのグループにしか入れない
        for n in range(self.N):
            self.prob += pulp.lpSum(self.x[n][g] for g in range(self.G)) == 1

    def set_group_num(self):
        # グループ内の人数はgroup_n_listに従う
        for g in range(self.G):
            self.prob += (
                pulp.lpSum(self.x[n][g] for n in range(self.N)) == self.group_n_list[g]
            )

    def set_young_num(self):
        # 各グループの若手の人数はyoung_n_listに従う
        for g in range(self.G):
            self.prob += (
                pulp.lpSum(
                    [self.x[n][g] for n in range(self.N) if self.age_list[n] == 0]
                )
                == self.young_n_list[g]
            )

    def set_team_overlap(self):
        # 各グループのチーム被りをできるだけ小さくする
        for g in range(self.G):
            for t in range(self.T):
                self.prob += (
                    pulp.lpSum(
                        [self.x[n][g] for n in range(self.N) if self.team_list[n] == t]
                    )
                    <= self.max_overlap
                )
                self.prob += (
                    pulp.lpSum(
                        [self.x[n][g] for n in range(self.N) if self.team_list[n] == t]
                    )
                    >= self.min_overlap
                )

    def set_young_team_overlap(self):
        # 各グループの若手内のチーム被りをできるだけ小さくする
        for g in range(self.G):
            for t in range(self.T):
                self.prob += (
                    pulp.lpSum(
                        [
                            self.x[n][g]
                            for n in range(self.N)
                            if self.team_list[n] == t and self.age_list[n] == 0
                        ]
                    )
                    <= self.max_young_overlap
                )
                self.prob += (
                    pulp.lpSum(
                        [
                            self.x[n][g]
                            for n in range(self.N)
                            if self.team_list[n] == t and self.age_list[n] == 0
                        ]
                    )
                    >= self.min_young_overlap
                )

    def set_old_team_overlap(self):
        # 各グループのベテランのチーム被りをできるだけ小さくする
        for g in range(self.G):
            for t in range(self.T):
                self.prob += (
                    pulp.lpSum(
                        [
                            self.x[n][g]
                            for n in range(self.N)
                            if self.team_list[n] == t and self.age_list[n] == 1
                        ]
                    )
                    <= self.max_old_overlap
                )
                self.prob += (
                    pulp.lpSum(
                        [
                            self.x[n][g]
                            for n in range(self.N)
                            if self.team_list[n] == t and self.age_list[n] == 1
                        ]
                    )
                    >= self.min_old_overlap
                )

    def set_young_team_overlap_with_old(self):
        # 各若手と同じグループのベテランのチーム被り数をできるだけ少なくする
        for g in range(self.G):
            for t in range(self.T):
                # y[g][t] = 1 ならば、gにtの若手が存在する
                # 定式化は以下を参考にした
                # https://www.msi.co.jp/solution/nuopt/docs/techniques/articles/indicator-variables.html
                self.prob += self.y[g][t] - self.group_n_list[g] * (
                    1 - self.y[g][t]
                ) <= pulp.lpSum(
                    [
                        self.x[n][g]
                        for n in range(self.N)
                        if self.team_list[n] == t and self.age_list[n] == 0
                    ]
                )
                self.prob += (
                    pulp.lpSum(
                        [
                            self.x[n][g]
                            for n in range(self.N)
                            if self.team_list[n] == t and self.age_list[n] == 0
                        ]
                    )
                    <= self.group_n_list[g] * self.y[g][t]
                )

                # gにtの若手が存在するとき、tのベテランの数はmax_young_overlap_with_old以下になるようにする。
                # なお、gにtの若手が存在しないときは、以下の式は必ず成り立つ。
                self.prob += (
                    self.group_n_list[g] * self.y[g][t]
                    + pulp.lpSum(
                        [
                            self.x[n][g]
                            for n in range(self.N)
                            if self.team_list[n] == t and self.age_list[n] == 1
                        ]
                    )
                    <= self.group_n_list[g] + self.max_young_overlap_with_old
                )

                # gにtの若手が存在するとき、tのベテランの数はmin_young_overlap_with_old以上になるようにする。
                # なお、gにtの若手が存在しないときは、以下の式は必ず成り立つ。
                self.prob += self.group_n_list[g] * self.y[g][
                    t
                ] + self.min_young_overlap_with_old <= self.group_n_list[
                    g
                ] + pulp.lpSum(
                    [
                        self.x[n][g]
                        for n in range(self.N)
                        if self.team_list[n] == t and self.age_list[n] == 1
                    ]
                )

    def solve(self):
        self.prob.solve()
        print(pulp.LpStatus[self.prob.status])


def solve_social_gathering(N, G, team_list, age_list):
    sg1 = SocialGathering(N, G, team_list, age_list)
    sg1.set_objective(sg1.max_young_overlap - sg1.min_young_overlap)
    sg1.set_only_one_group()
    sg1.set_group_num()
    sg1.set_young_num()
    sg1.set_young_team_overlap()
    sg1.solve()

    sg2 = SocialGathering(N, G, team_list, age_list)
    sg2.max_young_overlap = sg1.max_young_overlap.value()
    sg2.min_young_overlap = sg1.min_young_overlap.value()
    sg2.set_objective(sg2.max_young_overlap_with_old - sg2.min_young_overlap_with_old)
    sg2.set_only_one_group()
    sg2.set_group_num()
    sg2.set_young_num()
    sg2.set_young_team_overlap()
    sg2.set_young_team_overlap_with_old()
    sg2.solve()

    sg3 = SocialGathering(N, G, team_list, age_list)
    sg3.max_young_overlap = sg2.max_young_overlap
    sg3.min_young_overlap = sg2.min_young_overlap
    sg3.max_young_overlap_with_old = sg2.max_young_overlap_with_old.value()
    sg3.min_young_overlap_with_old = sg2.min_young_overlap_with_old.value()
    sg3.set_objective(sg3.max_old_overlap - sg3.min_old_overlap)
    sg3.set_only_one_group()
    sg3.set_group_num()
    sg3.set_young_num()
    sg3.set_young_team_overlap()
    sg3.set_young_team_overlap_with_old()
    sg3.set_old_team_overlap()
    sg3.solve()
    print(sg3.max_young_overlap)
    print(sg3.min_young_overlap)
    print(sg3.max_young_overlap_with_old)
    print(sg3.min_young_overlap_with_old)
    print(sg3.max_old_overlap.value())
    print(sg3.min_old_overlap.value())

    sg = sg3
    print(pulp.LpStatus[sg.prob.status])
    result_member = [[] for _ in range(G)]
    result_age = [[] for _ in range(G)]
    result_team = [[] for _ in range(G)]
    for g in range(G):
        for n in range(N):
            if pulp.value(sg.x[n][g]) == 1:
                result_member[g].append(n)
                result_age[g].append(age_list[n])
                result_team[g].append(team_list[n])

    for g in range(G):
        d = {}
        for i in range(len(result_team[g])):
            d[(result_team[g][i], result_age[g][i])] = (
                d.get((result_team[g][i], result_age[g][i]), 0) + 1
            )
        d = {k: v for k, v in d.items() if v > 1}
        print(f"グループ{g} 各(チーム,年層)ごとの人数:{d}")

    return result_member, result_age, result_team

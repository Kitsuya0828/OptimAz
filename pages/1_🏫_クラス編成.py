from sqlalchemy import column
import streamlit as st
import pandas as pd
import numpy as np
import pulp

st.set_page_config(
    page_title="クラス編成 | OptimAz",
    page_icon="images/favicon.png"
)

class_num = st.number_input('クラスの数を入力してください', min_value=1, max_value=26, value=8)

options = st.multiselect(
    '適用するルールを選択してください',
    ['男女比が均等', '学力試験の平均点', 'リーダー気質の生徒', '特別な支援が必要な生徒', '特定ペアを同一クラスに割り当てない', ],
    ['男女比が均等', '学力試験の平均点', 'リーダー気質の生徒', '特別な支援が必要な生徒', '特定ペアを同一クラスに割り当てない', ])

uploaded_files = st.file_uploader("CSVファイルをアップロードしてください", type=['csv',], accept_multiple_files=True)
if uploaded_files:
    with st.expander("アップロードしたデータの確認", expanded=False):
        for uploaded_file in uploaded_files:
            df = pd.read_csv(uploaded_file)
            if set(df.columns.values) == set(["student_id", "gender", "leader_flag", "support_flag", "score"]):
                st.session_state["s_df"] = df
            elif set(df.columns.values) == set(["student_id1", "student_id2"]):
                st.session_state["s_pair_df"] = df
            else:
                st.error("データのカラムに不備があります", icon="🚨")
                break
            st.caption(uploaded_file.name)
            st.dataframe(df)

    def solve(s_df, s_pair_df, class_num, options):
        prob = pulp.LpProblem('ClassAssignmentProblem', pulp.LpMaximize)

        # 生徒のリスト
        S = s_df['student_id'].tolist()
        
        # クラスのリスト（A～Z）
        C = [chr(65 + i) for i in range(class_num)]

        # 生徒とクラスのペアのリスト
        SC = [(s,c) for s in S for c in C]

        # 生徒をどのクラスに割り当てるを変数として定義
        x = pulp.LpVariable.dicts('x', SC, cat='Binary')

        # (1)各生徒は１つのクラスに割り当てる
        for s in S:
            prob += pulp.lpSum([x[s,c] for c in C]) == 1

        # (2)各クラスに均等に生徒の人数を割り当てる。
        for c in C:
            prob += pulp.lpSum([x[s,c] for s in S]) >= len(S) // class_num
            prob += pulp.lpSum([x[s,c] for s in S]) <= (len(S) + (class_num - 1)) // class_num

        if "男女均等" in options:
            # 男子生徒のリスト
            S_male = [row.student_id for row in s_df.itertuples() if row.gender == 1]

            # 女子生徒のリスト
            S_female = [row.student_id for row in s_df.itertuples() if row.gender == 0]

            # (3) 各クラスの男子生徒、女子生徒の人数は20人以下とする。
            for c in C:
                prob += pulp.lpSum([x[s,c] for s in S_male]) <= (len(S_male) + (class_num - 1)) // class_num
                prob += pulp.lpSum([x[s,c] for s in S_female]) <= (len(S_female) + (class_num - 1)) // class_num

        if "学力試験の平均点" in options:
            # 学力を辞書表現に変換
            score = {row.student_id:row.score for row in s_df.itertuples()}

            # 平均点の算出
            score_mean = s_df['score'].mean()

            # (4) 各クラスの学力試験の平均点は学年平均点±10点とする。      
            for c in C:
                prob += pulp.lpSum([x[s,c]*score[s] for s in S]) >= (score_mean - 10) * pulp.lpSum([x[s,c] for s in S])
                prob += pulp.lpSum([x[s,c]*score[s] for s in S]) <= (score_mean + 10) * pulp.lpSum([x[s,c] for s in S])

        if "リーダー気質の生徒" in options:
            # リーダー気質の生徒の集合
            S_leader = [row.student_id for row in s_df.itertuples() if row.leader_flag == 1]

            # (5)各クラスにリーダー気質の生徒を均等に割り当てる。
            for c in C:
                prob += pulp.lpSum([x[s,c] for s in S_leader]) >= len(S_leader) // class_num

        if "特別な支援が必要な生徒" in options:
            # 特別な支援が必要な生徒の集合
            S_support = [row.student_id for row in s_df.itertuples() if row.support_flag == 1]

            # (6) 特別な支援が必要な生徒を各クラスに均等に割り当てる
            for c in C:
                prob += pulp.lpSum([x[s,c] for s in S_support]) >= len(S_support) // class_num

        if "特定ペアを同一クラスに割り当てない" in options:
            # 生徒の特定ペアリスト
            SS = [(row.student_id1, row.student_id2) for row in s_pair_df.itertuples()]

            # (7) 特定ペアの生徒は同一クラスに割り当てない。
            for s1, s2 in SS:
                for c in C:
                    prob += x[s1,c] + x[s2,c] <= 1

        if "学力試験の平均点" in options:
            # 初期クラス編成を作成
            s_df['score_rank'] = s_df['score'].rank(ascending=False, method='first')
            class_dic = dict(zip(range(class_num), C))
            s_df['init_assigned_class'] = s_df['score_rank'].map(lambda x:x % class_num).map(class_dic)
            init_flag = {(s,c): 0 for s in S for c in C}
            for row in s_df.itertuples():
                init_flag[row.student_id, row.init_assigned_class] = 1
            
            # 目的関数:初期クラス編成と最適化結果のクラス編成をできるだけ一致させる
            prob += pulp.lpSum([x[s,c] * init_flag[s,c] for s,c in SC])        

        # 求解        
        status = prob.solve()
        print('Status:', pulp.LpStatus[status])

        # 最適化結果の表示
        # 各クラスに割り当てられている生徒のリストを辞書に格納
        C2Ss = {}
        result_list = []
        for c in C:
            C2Ss[c] = [str(s) for s in S if x[s,c].value()==1]
            result_list.append(C2Ss[c])
        
        
        result_df = pd.DataFrame(result_list, index=C).T
        st.dataframe(result_df)
        
        @st.cache
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(result_df)

        st.download_button(
            label="結果をダウンロード",
            data=csv,
            file_name='result.csv',
            mime='text/csv',
        )

        # for c, Ss in C2Ss.items():
        #     st.write('Class:', c)
        #     st.write('Num:', len(Ss))
        #     st.write('Student:', Ss)
    
    solve(st.session_state["s_df"], st.session_state["s_pair_df"], class_num, options)

st.sidebar.header("アップロードするデータについて")
st.sidebar.markdown("""
後日追記予定
""")
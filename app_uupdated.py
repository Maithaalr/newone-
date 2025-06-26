import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f5f8fc;
    }
    .metric-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
    }
    .section-header {
        font-size: 20px;
        color: #1e3d59;
        margin-top: 20px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

col_logo, col_upload = st.columns([1, 3])

with col_logo:
    logo = Image.open("logo.png")
    st.image(logo, width=180)

with col_upload:
    st.markdown("<div class='section-header'>يرجى تحميل بيانات الموظفين</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=0)
    selected_sheet = st.selectbox("اختر الجهة", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]

    # استبعاد الجهات التالية من التحليل
    excluded_departments = [
        'HC.نادي عجمان للفروسية',
        'PD.الشرطة المحلية لإمارة عجمان',
        'RC.الديوان الأميري'
    ]

    if 'الدائرة' in df.columns:
        df = df[~df['الدائرة'].isin(excluded_departments)]

    from datetime import datetime
    def calculate_age(birthdate):
        if pd.isnull(birthdate):
            return None
        return datetime.now().year - pd.to_datetime(birthdate).year

    if "تاريخ الميلاد" in df.columns:
        df["العمر"] = df["تاريخ الميلاد"].apply(calculate_age)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([" نظرة عامة", " تحليلات بصرية", " البيانات المفقودة", " عرض البيانات", " الموظفون فوق 60"])


    # ---------------- Tab 1 ---------------- #
    with tab1:
        st.markdown("###  نظرة عامة للموظفين المواطنين فقط")

        df_citizens = df[df['الجنسية'] == 'إماراتية'].copy()
        total = df_citizens.shape[0]
        excluded_cols = ['رقم الأقامة', 'الكفيل', 'تاريخ اصدار اللإقامة', 'تاريخ انتهاء اللإقامة']
        df_citizens_checked = df_citizens.drop(columns=[col for col in excluded_cols if col in df_citizens.columns])
        complete = df_citizens_checked.dropna().shape[0]
        missing_total = total - complete
        complete_pct = round((complete / total) * 100, 1) if total else 0
        missing_pct = round((missing_total / total) * 100, 1) if total else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-box' style='background-color:#1e3d59;'><h4> عدد المواطنين</h4><h2>{total}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box' style='background-color:#2a4d6f;'><h4> السجلات المكتملة</h4><h2>{complete} ({complete_pct}%)</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box' style='background-color:#4a7ca8;'><h4> السجلات الناقصة</h4><h2>{missing_total} ({missing_pct}%)</h2></div>", unsafe_allow_html=True)

        st.markdown("###  نظرة عامة للموظفين الوافدين فقط")

        df_non_citizens = df[df['الجنسية'] != 'إماراتية'].copy()
        total_non = df_non_citizens.shape[0]
        required_cols = ['رقم الأقامة', 'الكفيل', 'تاريخ اصدار اللإقامة', 'تاريخ انتهاء اللإقامة']
        present_required_cols = [col for col in required_cols if col in df_non_citizens.columns]
        is_complete = df_non_citizens[present_required_cols].notnull().all(axis=1)
        complete_non = is_complete.sum()
        missing_non = total_non - complete_non
        complete_non_pct = round((complete_non / total_non) * 100, 1) if total_non else 0
        missing_non_pct = round((missing_non / total_non) * 100, 1) if total_non else 0

        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown(f"<div class='metric-box' style='background-color:#1e3d59;'><h4> عدد الوافدين</h4><h2>{total_non}</h2></div>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<div class='metric-box' style='background-color:#2a4d6f;'><h4> السجلات المكتملة</h4><h2>{complete_non} ({complete_non_pct}%)</h2></div>", unsafe_allow_html=True)
        with col6:
            st.markdown(f"<div class='metric-box' style='background-color:#4a7ca8;'><h4> السجلات الناقصة</h4><h2>{missing_non} ({missing_non_pct}%)</h2></div>", unsafe_allow_html=True)

    # ---------------- Tab 2 ---------------- #
    with tab2:
        st.markdown("###  التحليلات البصرية")

        col1, col2 = st.columns(2)

        with col1:
            if 'الجنس' in df.columns:
                gender_counts = df['الجنس'].value_counts().reset_index()
                gender_counts.columns = ['الجنس', 'العدد']
                fig_gender = px.bar(gender_counts, x='الجنس', y='العدد',
                                    color='الجنس',
                                    color_discrete_sequence=['#2F4156', '#567C8D'])
                fig_gender.update_layout(title='توزيع الموظفين حسب الجنس', title_x=0.5)
                st.plotly_chart(fig_gender, use_container_width=True)

        with col2:
            if 'الديانة' in df.columns:
                religion_counts = df['الديانة'].value_counts().reset_index()
                religion_counts.columns = ['الديانة', 'العدد']
                fig_religion = px.bar(religion_counts, x='الديانة', y='العدد',
                                      color='الديانة',
                                      color_discrete_sequence=['#2F4156', '#567C8D'])
                fig_religion.update_layout(title='توزيع الموظفين حسب الديانة', title_x=0.5)
                st.plotly_chart(fig_religion, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            if 'الدائرة' in df.columns:
                dept_counts = df['الدائرة'].value_counts()
                fig_dept = go.Figure(data=[go.Pie(labels=dept_counts.index,
                                                  values=dept_counts.values,
                                                  hole=0.4,
                                                  marker=dict(colors=px.colors.sequential.Blues),
                                                  textinfo='label+percent')])
                fig_dept.update_layout(title='نسبة الموظفين حسب الدائرة', title_x=0.5)
                st.plotly_chart(fig_dept, use_container_width=True)

        with col4:

            if 'العمر' in df.columns:
                fig_hist = px.histogram(df, x='العمر', nbins=10,
                                        color_discrete_sequence=['#2F4156'])
                fig_hist.update_layout(title='Histogram - توزيع الأعمار', title_x=0.5)
                st.plotly_chart(fig_hist, use_container_width=True)

            if 'العمر' in df.columns:
                # تقسيم الأعمار إلى 20 فئة تلقائيًا
                df['فئة العمر'] = pd.cut(df['العمر'], bins=20)

                # استخراج الفئة كنص بسيط (مثل: "30-34")
                age_counts = df['فئة العمر'].value_counts().sort_index().reset_index()
                age_counts.columns = ['الفئة', 'العدد']
                age_counts['النسبة'] = round((age_counts['العدد'] / age_counts['العدد'].sum()) * 100, 1)
                age_counts['الفئة النصية'] = age_counts['الفئة'].apply(lambda x: f"{int(x.left)}-{int(x.right)}")

                # النص الكامل للعرض
                age_counts['التسمية'] = age_counts.apply(
                    lambda row: f"{row['الفئة النصية']} | {row['العدد']} ({row['النسبة']}%)", axis=1
                )

                # رسم الرسم البياني
                fig_bar = px.bar(
                    age_counts,
                    x='الفئة النصية',
                    y='العدد',
                    text='التسمية',
                    color='العدد',
                    color_continuous_scale=['#C8D9E6', '#2F4156']
                )

                fig_bar.update_traces(
                    textposition='outside',
                    textangle=0,
                    textfont_size=11
                )

                fig_bar.update_layout(title='Bar Chart - توزيع الأعمار مع الفئة والعدد والنسبة', title_x=0.5, xaxis_tickangle=-45, yaxis_title='العدد', xaxis_title='الفئة العمرية')
                st.plotly_chart(fig_bar, use_container_width=True)

        col5, col6 = st.columns(2)

        with col5:
            if 'المستوى التعليمي' in df.columns:
                edu_counts = df['المستوى التعليمي'].value_counts().reset_index()
                edu_counts.columns = ['المستوى التعليمي', 'العدد']
                fig_tree = px.treemap(edu_counts, path=['المستوى التعليمي'], values='العدد',
                                      color_discrete_sequence=['#2F4156', '#567C8D'])
                fig_tree.update_layout(title='Treemap - المستوى التعليمي', title_x=0.5)
                st.plotly_chart(fig_tree, use_container_width=True)

        with col6:
            if 'الجنس' in df.columns and 'العمر' in df.columns:
                fig_box = px.box(df, x='الجنس', y='العمر', color='الجنس',
                                 color_discrete_sequence=['#2F4156', '#C8D9E6'])
                fig_box.update_layout(title='Boxplot - العمر حسب الجنس', title_x=0.5)
                st.plotly_chart(fig_box, use_container_width=True)


    # ---------------- Tab 3 ---------------- #
    with tab3:
        st.markdown("###  تحليل البيانات المفقودة")

        # Split into citizens and non-citizens
        df_citizens = df[df['الجنسية'] == 'إماراتية'].copy()
        df_non_citizens = df[df['الجنسية'] != 'إماراتية'].copy()

        st.subheader(" نواقص المواطنين ")
        excluded_cols = ['رقم الأقامة', 'الكفيل', 'تاريخ اصدار اللإقامة', 'تاريخ انتهاء اللإقامة']
        filtered_citizen_df = df_citizens.drop(columns=[col for col in excluded_cols if col in df_citizens.columns])
        missing_percent_c = filtered_citizen_df.isnull().mean() * 100
        missing_count_c = filtered_citizen_df.isnull().sum()

        missing_df_c = pd.DataFrame({
            'العمود': filtered_citizen_df.columns,
            'عدد القيم المفقودة': missing_count_c,
            'النسبة المئوية': missing_percent_c
        }).query("`عدد القيم المفقودة` > 0")

        fig_c = px.bar(
            missing_df_c,
            x='العمود',
            y='عدد القيم المفقودة',
            color='النسبة المئوية',
            text=missing_df_c.apply(lambda row: f"{row['عدد القيم المفقودة']} | {round(row['النسبة المئوية'], 1)}%", axis=1),
            color_continuous_scale=['#C8D9E6', '#2F4156']
        )
        fig_c.update_layout(title="المواطنين - عدد القيم المفقودة ونسبتها", title_x=0.5, xaxis_tickangle=-45)
        st.plotly_chart(fig_c, use_container_width=True)

        st.subheader(" نواقص الوافدين ")
        
        df_non_citizens = df[df['الجنسية'] != 'إماراتية'].copy()
        missing_percent_n = df_non_citizens.isnull().mean() * 100
        missing_count_n = df_non_citizens.isnull().sum()

        missing_df_n = pd.DataFrame({
            'العمود': df_non_citizens.columns,
            'عدد القيم المفقودة': missing_count_n,
            'النسبة المئوية': missing_percent_n
        }).query("`عدد القيم المفقودة` > 0")

        fig_n = px.bar(
            missing_df_n,
            x='العمود',
            y='عدد القيم المفقودة',
            color='النسبة المئوية',
            text=missing_df_n.apply(lambda row: f"{row['عدد القيم المفقودة']} | {round(row['النسبة المئوية'], 1)}%", axis=1),
            color_continuous_scale=['#C8D9E6', '#2F4156']
        )
        fig_n.update_layout(title="الوافدين - عدد القيم المفقودة ونسبتها", title_x=0.5, xaxis_tickangle=-45)
        st.plotly_chart(fig_n, use_container_width=True)

        st.markdown("###  تحليل مفقودات عمود محدد")
        selected_column = st.selectbox("اختر عمود", df.columns)

        if selected_column:
            total = df.shape[0]
            missing = df[selected_column].isnull().sum()
            present = total - missing

            values = [present, missing]
            labels = ['موجودة', 'مفقودة']

            fig_donut = px.pie(
                names=labels,
                values=values,
                hole=0.5,
                color=labels,
                color_discrete_map={
                    'مفقودة': '#C8D9E6',
                    'موجودة': '#2F4156'
                }
            )
            fig_donut.update_traces(
                text=[f'{v} | {round(v/total*100)}%' for v in values],
                textinfo='text+label'
            )
            fig_donut.update_layout(title=f"نسبة البيانات في العمود: {selected_column}", title_x=0.5)
            st.plotly_chart(fig_donut, use_container_width=True)

    # ---------------- Tab 4 ---------------- #
    with tab4:
        st.markdown("<div class='section-header'> فلترة حسب القيم</div>", unsafe_allow_html=True)
        filter_cols = st.multiselect("اختر أعمدة للفلترة:", df.columns)
        filtered_df = df.copy()
        for col in filter_cols:
            options = df[col].dropna().unique().tolist()
            selected = st.multiselect(f"{col}", options)
            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]

        st.markdown("<div class='section-header'> البيانات بعد الفلترة</div>", unsafe_allow_html=True)
        st.dataframe(filtered_df)


    # ---------------- Tab 5 ---------------- #
    with tab5:
        st.subheader(" الموظفون الذين أعمارهم فوق 60 سنة")
    
        over_60 = df[df["العمر"] > 60]

        if not over_60.empty:
            st.dataframe(over_60, use_container_width=True)
            st.success(f"عدد الموظفين فوق سن 60: {len(over_60)}")

            # زر تحميل البيانات
            st.download_button(
                label=" تحميل البيانات كـ CSV",
                data=over_60.to_csv(index=False).encode("utf-8"),
                file_name="الموظفون_فوق_60.csv",
                mime="text/csv"
            )
        else:
            st.info("لا يوجد موظفون أعمارهم فوق 60 سنة.")


    # --------------- Sidebar Introduction ---------------- #
    st.sidebar.markdown("## مرحباً بك في لوحة معلومات الموظفين")
    st.sidebar.write("""
    هذه اللوحة تتيح لك:
    - تحليل شامل لبيانات الموظفين
    - عرض بصري تفاعلي
    - تقييم جودة البيانات
    - وإمكانية الفلترة المتقدمة
    """)

    # Optional Export from Tab 4
    if not filtered_df.empty:
        st.sidebar.markdown("###  تحميل البيانات بعد الفلترة")
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button(
            label="تحميل CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv'
        )
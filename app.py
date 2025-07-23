import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Sertifikasi", layout="wide")
st.title("📊 DASHBOARD  SERTIFIKASI SELAMA 6 BULAN TERAKHIR")

# --- Load Data ---
df = pd.read_excel("Cleaned_FullRecap.xlsx")
df['Tanggal Sertifikasi'] = pd.to_datetime(df['Tanggal Sertifikasi'], dayfirst=True, errors='coerce')

# --- Filter Data Aktif ---
df_aktif = df[df['Pendaftar'] > 0].copy()

# --- Buat Kolom Bulan ---
df_aktif['Bulan'] = df_aktif['Tanggal Sertifikasi'].dt.to_period('M').astype(str)

# === VISUAL 1: Total Pendaftar per Bulan ===
st.subheader("📅 TOTAL PENDAFTAR PERBULAN (6 bulan terakhir)")

# Dropdown filter jenis total yang ditampilkan
opsi_total = st.radio("Pilih Data yang Ditampilkan:", ["Pendaftar", "Selesai", "Dibatalkan"], horizontal=True)

if opsi_total == "Pendaftar":
    data_total = df_aktif.groupby('Bulan')['Pendaftar'].sum().reset_index()
    total_value = df_aktif['Pendaftar'].sum()
elif opsi_total == "Selesai":
    data_total = df_aktif.groupby('Bulan')['Selesai'].sum().reset_index()
    total_value = df_aktif['Selesai'].sum()
else:
    data_total = df_aktif.groupby('Bulan')['Dibatalkan'].sum().reset_index()
    total_value = df_aktif['Dibatalkan'].sum()

st.markdown(f"**Total {opsi_total}: `{total_value}` orang**")

fig_bulan = px.bar(
    data_total,
    x='Bulan',
    y=opsi_total,
    text=opsi_total,
    title=f'Total {opsi_total} sertifikasi perbulan'
)
fig_bulan.update_traces(textposition='outside')
fig_bulan.update_layout(xaxis_title='Bulan', yaxis_title=f'Jumlah {opsi_total}')

st.plotly_chart(fig_bulan, use_container_width=True)

# === VISUAL 2: Tren Pendaftar Instansi Tertentu ===
st.subheader("🏢 TREN PENDAFTAR DARI INSTANSI TERTENTU")

instansi_list = sorted(df_aktif['Instansi'].unique())
selected_instansi = st.selectbox("Pilih Instansi", instansi_list)

df_instansi = df_aktif[df_aktif['Instansi'] == selected_instansi].copy()
df_instansi['Tanggal Sertifikasi'] = pd.to_datetime(df_instansi['Tanggal Sertifikasi'])

# 👉 Tambahkan total pendaftar dari instansi ini
total_instansi = df_instansi['Pendaftar'].sum()
st.metric(label=f"Total Pendaftar dari {selected_instansi}", value=f"{total_instansi} orang", delta=None)

# Buat data tren
instansi_per_tanggal = df_instansi.groupby('Tanggal Sertifikasi')['Pendaftar'].sum().reset_index()

fig_instansi = px.line(
    instansi_per_tanggal,
    x='Tanggal Sertifikasi',
    y='Pendaftar',
    markers=True,
    title=f'Tren Jumlah Pendaftar dari {selected_instansi}'
)
fig_instansi.update_layout(
    xaxis_title='Tanggal Sertifikasi',
    yaxis_title='Jumlah Pendaftar',
    xaxis_tickformat='%d %b %Y'  # Format tanggal misal: 11 Feb 2025
)

st.plotly_chart(fig_instansi, use_container_width=True)

# === VISUAL 3: Pie Chart jenis sertifikasi ===
st.subheader("🧾 DISTRIBUSI JENIS SERTIFIKASI BERDASARKAN (PENDAFTARAN SELESAI)")

# Filter hanya data yang selesai
df_selesai = df_aktif[df_aktif['Selesai'] > 0]

opsi_kategori = st.selectbox("Pilih Kategori Visualisasi:", ["Jenis Sertifikasi", "Instansi"], key='kategori_pie')

if opsi_kategori == "Jenis Sertifikasi":
    pie_data = df_selesai.groupby('Jenis Sertifikasi')['Selesai'].sum().reset_index()
    fig_pie = px.pie(
        pie_data,
        names='Jenis Sertifikasi',
        values='Selesai',
        title='Distribusi Selesai Berdasarkan Jenis Sertifikasi'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

else:
    instansi_opsi = ['Semua'] + sorted(df_selesai['Instansi'].unique())
    selected_instansi = st.selectbox("Pilih Instansi", instansi_opsi, key='instansi_opsi')

    if selected_instansi == 'Semua':
        filtered_data = df_selesai
    else:
        filtered_data = df_selesai[df_selesai['Instansi'] == selected_instansi]

    pie_data = filtered_data.groupby('Jenis Sertifikasi')['Selesai'].sum().reset_index()
    fig_pie = px.pie(
        pie_data,
        names='Jenis Sertifikasi',
        values='Selesai',
        title=f'Distribusi Jenis Sertifikasi dari Instansi {selected_instansi}'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# === VISUAL 4: Top 5 Instansi ===
st.subheader("🏆 5 INSTANSI DENGAN JUMLAH PENDAFTAR TERBANYAK")

top_instansi_all = df_aktif.groupby('Instansi')['Pendaftar'].sum().nlargest(5).reset_index()
top_list = top_instansi_all['Instansi'].tolist()

selected_top = st.multiselect("Pilih Instansi untuk Ditampilkan:", top_list, default=top_list)

top_selected_df = top_instansi_all[top_instansi_all['Instansi'].isin(selected_top)]

fig_top_instansi = px.bar(
    top_selected_df,
    x='Pendaftar',
    y='Instansi',
    orientation='h',
    title='Top Instansi Berdasarkan Jumlah Pendaftar'
)
fig_top_instansi.update_layout(xaxis_title='Jumlah Pendaftar', yaxis_title='Instansi')

st.plotly_chart(fig_top_instansi, use_container_width=True)
# === PENUTUP DAN KESIMPULAN ===
with st.expander("📌 Penutup dan Kesimpulan"):
    st.markdown("""
    ### 🧾 **Penutup dan Kesimpulan**

    Dashboard ini menyajikan gambaran komprehensif mengenai **tren sertifikasi dalam 6 bulan terakhir**, mencakup total pendaftar, penyelesaian sertifikasi, serta pembatalan dari berbagai instansi dan jenis sertifikasi. Dari visualisasi yang telah ditampilkan, dapat disimpulkan beberapa hal penting:

    #### ✅ **Apa yang Terjadi:**
    - **Lonjakan pendaftar** terjadi pada bulan tertentu, menunjukkan antusiasme yang mungkin berkaitan dengan kebutuhan kompetensi musiman atau program internal instansi.
    - Beberapa instansi **secara konsisten aktif**, seperti *[instansi yang menonjol dari data]*, menunjukkan kemitraan yang kuat.
    - **Jenis sertifikasi tertentu lebih diminati**, terlihat dari proporsi pie chart.
    - Terdapat **instansi dengan rasio penyelesaian yang tinggi**, dan beberapa lainnya memiliki tingkat pembatalan signifikan.

    #### 🔍 **Apa yang Bisa Dilakukan:**
    - Fokus pada **pelatihan dan komunikasi lebih lanjut** kepada instansi dengan rasio pembatalan tinggi untuk memahami hambatan mereka.
    - Dorong instansi dengan partisipasi rendah namun potensial melalui **kampanye targeted** atau penawaran khusus.
    - Evaluasi **jenis sertifikasi populer** untuk dikembangkan lebih lanjut atau ditingkatkan kapasitasnya.

    #### 🧠 **Keputusan yang Bisa Diambil oleh Perusahaan:**
    - **Optimasi alokasi sumber daya** ke instansi dan jenis sertifikasi dengan tingkat penyelesaian tinggi.
    - **Tingkatkan kualitas layanan** pada bulan dengan lonjakan pendaftar untuk menghindari overload dan menjaga kepuasan peserta.
    - **Bangun kemitraan strategis** dengan instansi yang masuk Top 5 untuk menjajaki program jangka panjang.
    """)

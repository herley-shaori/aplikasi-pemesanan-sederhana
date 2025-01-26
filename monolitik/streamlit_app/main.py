import streamlit as st

def main():
    st.title("Order Form")

    default_payload = {
        "jenis_pesanan": "makanan",
        "id_pengguna": 789,
        "nama_pemesan": "Herley",
        "daftar_pesanan": [
            {
                "id_menu": 101,
                "nama_menu": "Nasi Goreng Spesial",
                "jumlah": 2
            },
            {
                "id_menu": 105,
                "nama_menu": "Es Teh Manis",
                "jumlah": 1
            }
        ],
        "metode_pembayaran": "tunai"
    }

    jenis_pesanan = st.text_input("Jenis Pesanan", default_payload["jenis_pesanan"])
    id_pengguna = st.number_input("ID Pengguna", value=default_payload["id_pengguna"], step=1)
    nama_pemesan = st.text_input("Nama Pemesan", default_payload["nama_pemesan"])
    metode_pembayaran = st.text_input("Metode Pembayaran", default_payload["metode_pembayaran"])

    st.subheader("Daftar Pesanan")
    daftar_pesanan = []
    num_items = st.number_input("Jumlah Item Pesanan", min_value=1, value=len(default_payload["daftar_pesanan"]), step=1)

    for i in range(num_items):
        st.write(f"**Item {i+1}**")
        if i < len(default_payload["daftar_pesanan"]):
            default_item = default_payload["daftar_pesanan"][i]
        else:
            default_item = {"id_menu": "", "nama_menu": "", "jumlah": 1}

        id_menu = st.number_input(f"ID Menu {i+1}", value=default_item["id_menu"], step=1, key=f"id_menu_{i}")
        nama_menu = st.text_input(f"Nama Menu {i+1}", value=default_item["nama_menu"], key=f"nama_menu_{i}")
        jumlah = st.number_input(f"Jumlah {i+1}", min_value=1, value=default_item["jumlah"], step=1, key=f"jumlah_{i}")

        daftar_pesanan.append({
            "id_menu": int(id_menu) if id_menu else None,
            "nama_menu": nama_menu,
            "jumlah": int(jumlah)
        })

    if st.button("Submit Request"):
        payload = {
            "jenis_pesanan": jenis_pesanan,
            "id_pengguna": int(id_pengguna),
            "nama_pemesan": nama_pemesan,
            "daftar_pesanan": daftar_pesanan,
            "metode_pembayaran": metode_pembayaran
        }
        st.write("Order Submitted!")
        st.write("Payload:")
        st.json(payload) # Display the constructed JSON payload

if __name__ == "__main__":
    main()
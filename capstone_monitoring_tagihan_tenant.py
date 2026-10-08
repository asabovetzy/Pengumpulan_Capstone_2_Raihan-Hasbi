# ==========================================================
# CAPSTONE PROJECT MODULE 2 - MONITORING TAGIHAN TENANT
# Primary key : Tenant ID (contoh T001)
# Field       : tenant_id, nama_tenant, unit, kategori, tagihan
# Catatan     : data di bawah adalah data dummy
#
# Fitur tambahan (tanpa mengubah flowchart):
#   1. Validasi input: format Tenant ID (T + 3 angka), Periode (DD-MM-YYYY),
#      kategori dipilih dari daftar, input berisi spasi saja ditolak
#   2. Satu unit tidak boleh ditempati dua tenant
#   3. Ringkasan statistik tagihan di menu Read
#   4. Detail tenant + peringatan tunggakan sebelum hapus di menu Delete
# ==========================================================

# ---------- DATA ----------
# Key luar = Tenant ID. 'tagihan' = list invoice milik tenant itu.
data_tenant = {
    'T001': {
        'nama_tenant': 'Kopi Sudut',
        'unit': 'GF-12',
        'kategori': 'F&B',
        'tagihan': [
            {'no_invoice': 'INV001', 'jenis': 'Sewa', 'periode': '01-09-2026', 'jumlah': 15000000, 'status': 'Lunas'},
            {'no_invoice': 'INV002', 'jenis': 'Service Charge', 'periode': '01-09-2026', 'jumlah': 2500000, 'status': 'Belum Lunas'}
        ]
    },
    'T002': {
        'nama_tenant': 'Roti Pagi',
        'unit': 'LG-05',
        'kategori': 'F&B',
        'tagihan': [
            {'no_invoice': 'INV003', 'jenis': 'Sewa', 'periode': '01-09-2026', 'jumlah': 12000000, 'status': 'Belum Lunas'}
        ]
    },
    'T003': {
        'nama_tenant': 'Mode Kita',
        'unit': 'UG-21',
        'kategori': 'Fashion',
        'tagihan': [
            {'no_invoice': 'INV004', 'jenis': 'Sewa', 'periode': '01-09-2026', 'jumlah': 20000000, 'status': 'Lunas'},
            {'no_invoice': 'INV005', 'jenis': 'Listrik', 'periode': '01-09-2026', 'jumlah': 3200000, 'status': 'Belum Lunas'}
        ]
    }
}

# Kolom yang boleh diubah (tenant_id tidak, karena primary key)
kolom_update = ['nama_tenant', 'unit', 'kategori', 'tagihan']

# Pilihan kategori tenant
daftar_kategori = ['F&B', 'Fashion', 'Entertainment', 'Elektronik', 'Lainnya']


# ---------- FUNCTION BANTUAN (VALIDASI INPUT) ----------
def hanya_spasi(teks):
    # True kalau teks kosong atau isinya spasi semua
    for karakter in teks:
        if karakter != ' ':
            return False
    return True


def input_tidak_kosong(pesan):
    # Minta input sampai tidak kosong (spasi saja juga dianggap kosong)
    teks = input(pesan)
    while hanya_spasi(teks):
        print('Input tidak boleh kosong.')
        teks = input(pesan)
    return teks


def semua_angka(teks):
    # True kalau teks tidak kosong dan semua karakternya angka 0-9
    if teks == '':
        return False
    for karakter in teks:
        if karakter not in '0123456789':
            return False
    return True


def input_angka(pesan):
    # Minta input sampai berupa angka lebih dari 0
    teks = input(pesan)
    while not semua_angka(teks) or int(teks) <= 0:
        print('Input harus berupa angka lebih dari 0.')
        teks = input(pesan)
    return int(teks)


def input_ya_tidak(pesan):
    # Minta input sampai dijawab y atau n
    jawaban = input(pesan).lower()
    while jawaban != 'y' and jawaban != 'n':
        print('Jawab dengan y atau n.')
        jawaban = input(pesan).lower()
    return jawaban


def input_status():
    # Pilih status pakai angka supaya tulisannya seragam
    pilihan = input('Status (1. Belum Lunas / 2. Lunas): ')
    while pilihan != '1' and pilihan != '2':
        print('Pilih 1 atau 2.')
        pilihan = input('Status (1. Belum Lunas / 2. Lunas): ')
    if pilihan == '1':
        return 'Belum Lunas'
    else:
        return 'Lunas'


def input_kategori():
    # Pilih kategori pakai angka supaya tulisannya seragam (F&B tidak jadi f&b)
    for i in range(len(daftar_kategori)):
        print('{}. {}'.format(i + 1, daftar_kategori[i]))
    pesan = 'Pilih kategori (1-{}): '.format(len(daftar_kategori))
    pilihan = input(pesan)
    while not semua_angka(pilihan) or int(pilihan) < 1 or int(pilihan) > len(daftar_kategori):
        print('Pilih angka 1 sampai {}.'.format(len(daftar_kategori)))
        pilihan = input(pesan)
    return daftar_kategori[int(pilihan) - 1]


# ---------- FITUR TAMBAHAN 1: VALIDASI FORMAT ----------
def format_tenant_id_benar(tenant_id):
    # Format benar: T + 3 angka, contoh T001
    if len(tenant_id) != 4:
        return False
    if tenant_id[0] != 'T':
        return False
    if not semua_angka(tenant_id[1:]):
        return False
    return True


def input_tenant_id(pesan):
    # Minta Tenant ID sampai formatnya benar (dipakai di semua menu)
    tenant_id = input(pesan).upper()
    while not format_tenant_id_benar(tenant_id):
        print('Format Tenant ID salah. Harus huruf T + 3 angka, contoh T004.')
        tenant_id = input(pesan).upper()
    return tenant_id


def format_periode_benar(periode):
    # Format benar: DD-MM-YYYY dan tanggalnya ada di kalender
    if len(periode) != 10:
        return False
    if periode[2] != '-' or periode[5] != '-':
        return False
    hari = periode[:2]
    bulan = periode[3:5]
    tahun = periode[6:]
    if not semua_angka(hari) or not semua_angka(bulan) or not semua_angka(tahun):
        return False
    if int(bulan) < 1 or int(bulan) > 12:
        return False
    if int(tahun) < 2000 or int(tahun) > 2100:
        return False

    # Jumlah hari tiap bulan (index 0 = Januari). Tahun kabisat: Februari 29 hari.
    hari_per_bulan = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if int(tahun) % 4 == 0 and (int(tahun) % 100 != 0 or int(tahun) % 400 == 0):
        hari_per_bulan[1] = 29
    if int(hari) < 1 or int(hari) > hari_per_bulan[int(bulan) - 1]:
        return False
    return True


def input_periode():
    # Minta periode sampai formatnya benar
    periode = input('Periode (DD-MM-YYYY, contoh 01-09-2026): ')
    while not format_periode_benar(periode):
        print('Format periode salah. Contoh yang benar: 01-09-2026, dan tanggalnya harus ada di kalender.')
        periode = input('Periode (DD-MM-YYYY, contoh 01-09-2026): ')
    return periode


# ---------- FUNCTION BANTUAN (TAGIHAN) ----------
def cek_no_invoice(no_invoice):
    # True kalau nomor invoice sudah dipakai tenant mana pun
    for tenant_id in data_tenant:
        for tagihan in data_tenant[tenant_id]['tagihan']:
            if tagihan['no_invoice'] == no_invoice:
                return True
    return False


def hitung_belum_lunas(daftar_tagihan):
    # Jumlah semua tagihan yang statusnya Belum Lunas
    total = 0
    for tagihan in daftar_tagihan:
        if tagihan['status'] == 'Belum Lunas':
            total += tagihan['jumlah']
    return total


def input_tagihan_baru():
    # Minta data 1 invoice, kembalikan sebagai dictionary
    no_invoice = input_tidak_kosong('No Invoice: ').upper()
    while cek_no_invoice(no_invoice):
        print('No Invoice sudah dipakai.')
        no_invoice = input_tidak_kosong('No Invoice: ').upper()
    jenis = input_tidak_kosong('Jenis tagihan (Sewa/Service Charge/Listrik): ')
    periode = input_periode()   # fitur tambahan 1
    jumlah = input_angka('Jumlah tagihan (Rp): ')
    status = input_status()
    return {'no_invoice': no_invoice, 'jenis': jenis, 'periode': periode, 'jumlah': jumlah, 'status': status}


# ---------- FITUR TAMBAHAN 2: UNIT TIDAK BOLEH DOBEL ----------
def cari_pemilik_unit(unit):
    # Tenant ID yang menempati unit itu, atau '' kalau unit kosong
    for tenant_id in data_tenant:
        if data_tenant[tenant_id]['unit'] == unit:
            return tenant_id
    return ''


def input_unit(pesan, tenant_id_sendiri):
    # Minta unit sampai tidak dipakai tenant lain (unit milik sendiri boleh)
    unit = input_tidak_kosong(pesan).upper()
    pemilik = cari_pemilik_unit(unit)
    while pemilik != '' and pemilik != tenant_id_sendiri:
        print('Unit {} sudah ditempati {} ({}).'.format(
            unit, data_tenant[pemilik]['nama_tenant'], pemilik))
        unit = input_tidak_kosong(pesan).upper()
        pemilik = cari_pemilik_unit(unit)
    return unit


# ---------- FUNCTION TAMPILAN ----------
def tampil_semua_tenant():
    print('\nDaftar Tenant')
    print('Tenant ID | Nama Tenant | Unit | Kategori | Jumlah Invoice | Total Belum Lunas')
    for tenant_id, tenant in data_tenant.items():
        print('{} | {} | {} | {} | {} | Rp {}'.format(
            tenant_id,
            tenant['nama_tenant'],
            tenant['unit'],
            tenant['kategori'],
            len(tenant['tagihan']),
            hitung_belum_lunas(tenant['tagihan'])
        ))


def tampil_detail_tenant(tenant_id):
    # Tampilkan 1 tenant beserta semua invoicenya
    tenant = data_tenant[tenant_id]
    print('\nTenant ID   : {}'.format(tenant_id))
    print('Nama Tenant : {}'.format(tenant['nama_tenant']))
    print('Unit        : {}'.format(tenant['unit']))
    print('Kategori    : {}'.format(tenant['kategori']))
    print('Daftar Tagihan:')
    if len(tenant['tagihan']) == 0:
        print('  (belum ada tagihan)')
    else:
        print('  No Invoice | Jenis | Periode | Jumlah | Status')
        for tagihan in tenant['tagihan']:
            print('  {} | {} | {} | Rp {} | {}'.format(
                tagihan['no_invoice'],
                tagihan['jenis'],
                tagihan['periode'],
                tagihan['jumlah'],
                tagihan['status']
            ))
    print('Total Belum Lunas: Rp {}'.format(hitung_belum_lunas(tenant['tagihan'])))


# ---------- FITUR TAMBAHAN 3: RINGKASAN STATISTIK ----------
def tampil_statistik():
    jumlah_invoice = 0
    total_tagihan = 0
    total_lunas = 0
    tunggakan_terbesar = 0
    tenant_terbesar = ''
    per_kategori = {}

    for tenant_id, tenant in data_tenant.items():
        belum_lunas_tenant = hitung_belum_lunas(tenant['tagihan'])

        # Cari tenant dengan tunggakan terbesar
        if belum_lunas_tenant > tunggakan_terbesar:
            tunggakan_terbesar = belum_lunas_tenant
            tenant_terbesar = tenant_id

        # Total tunggakan per kategori
        kategori = tenant['kategori']
        if kategori not in per_kategori:
            per_kategori[kategori] = 0
        per_kategori[kategori] += belum_lunas_tenant

        for tagihan in tenant['tagihan']:
            jumlah_invoice += 1
            total_tagihan += tagihan['jumlah']
            if tagihan['status'] == 'Lunas':
                total_lunas += tagihan['jumlah']

    total_belum_lunas = total_tagihan - total_lunas

    print('\n--- Ringkasan ---')
    print('Jumlah tenant       : {}'.format(len(data_tenant)))
    print('Jumlah invoice      : {}'.format(jumlah_invoice))
    print('Total tagihan       : Rp {}'.format(total_tagihan))

    if total_tagihan > 0:   # hindari pembagian dengan 0
        persen_lunas = total_lunas * 100 // total_tagihan
        print('Sudah lunas         : Rp {} ({}%)'.format(total_lunas, persen_lunas))
        print('Belum lunas         : Rp {} ({}%)'.format(total_belum_lunas, 100 - persen_lunas))

    if tenant_terbesar == '':
        print('Tunggakan terbesar  : tidak ada, semua sudah lunas')
    else:
        print('Tunggakan terbesar  : {} ({}) - Rp {}'.format(
            data_tenant[tenant_terbesar]['nama_tenant'], tenant_terbesar, tunggakan_terbesar))

    print('Tunggakan per kategori:')
    for kategori, total in per_kategori.items():
        print('  {} : Rp {}'.format(kategori, total))


# ---------- MENU READ ----------
def menu_read():
    while True:
        print('\n=== Menu Tampilkan Data ===')
        print('1. Tampilkan semua tenant')
        print('2. Tampilkan tagihan berdasarkan Tenant ID')
        print('3. Kembali ke menu utama')
        pilihan = input('Pilih menu (1-3): ')

        if pilihan == '1':
            if len(data_tenant) == 0:
                print('Data tidak ada')
            else:
                tampil_semua_tenant()
                tampil_statistik()   # fitur tambahan 3
        elif pilihan == '2':
            if len(data_tenant) == 0:
                print('Data tidak ada')
            else:
                tenant_id = input_tenant_id('Masukkan Tenant ID: ')  # fitur tambahan 1
                if tenant_id in data_tenant:
                    tampil_detail_tenant(tenant_id)
                else:
                    print('Data tidak ada')
        elif pilihan == '3':
            break
        else:
            print('Pilihan yang Anda masukkan tidak valid')


# ---------- MENU CREATE ----------
def menu_create():
    while True:
        print('\n=== Menu Tambah Data ===')
        print('1. Tambah tenant baru')
        print('2. Kembali ke menu utama')
        pilihan = input('Pilih menu (1-2): ')

        if pilihan == '1':
            tenant_id = input_tenant_id('Masukkan Tenant ID (contoh T004): ')  # fitur tambahan 1
            if tenant_id in data_tenant:
                print('Data sudah ada')
            else:
                nama_tenant = input_tidak_kosong('Nama Tenant: ')
                unit = input_unit('Unit: ', tenant_id)   # fitur tambahan 2
                print('Kategori:')
                kategori = input_kategori()
                print('Isi tagihan pertama untuk tenant ini')
                tagihan_baru = input_tagihan_baru()

                simpan = input_ya_tidak('Simpan data? (y/n): ')
                if simpan == 'y':
                    data_tenant[tenant_id] = {
                        'nama_tenant': nama_tenant,
                        'unit': unit,
                        'kategori': kategori,
                        'tagihan': [tagihan_baru]
                    }
                    print('Data berhasil disimpan')
                else:
                    print('Data batal disimpan')
        elif pilihan == '2':
            break
        else:
            print('Pilihan yang Anda masukkan tidak valid')


# ---------- MENU UPDATE ----------
def menu_update():
    while True:
        print('\n=== Menu Ubah Data ===')
        print('1. Ubah data tenant')
        print('2. Kembali ke menu utama')
        pilihan = input('Pilih menu (1-2): ')

        if pilihan == '1':
            tenant_id = input_tenant_id('Masukkan Tenant ID: ')  # fitur tambahan 1
            if tenant_id not in data_tenant:
                print('Data yang Anda cari tidak ada')
            else:
                tampil_detail_tenant(tenant_id)
                lanjut = input_ya_tidak('Lanjut ubah data? (y/n): ')
                if lanjut == 'y':
                    # User memasukkan nama kolom yang mau diubah
                    print('Kolom yang bisa diubah: {}'.format(kolom_update))
                    kolom = input('Masukkan nama kolom: ').lower()
                    while kolom not in kolom_update:
                        print('Kolom tidak ada atau tidak boleh diubah.')
                        kolom = input('Masukkan nama kolom: ').lower()

                    # User memasukkan nilai baru (belum disimpan dulu)
                    daftar_tagihan = data_tenant[tenant_id]['tagihan']
                    aksi = ''
                    if kolom == 'unit':
                        nilai_baru = input_unit('Masukkan unit baru: ', tenant_id)   # fitur tambahan 2
                    elif kolom == 'kategori':
                        print('Kategori baru:')
                        nilai_baru = input_kategori()
                    elif kolom != 'tagihan':
                        nilai_baru = input_tidak_kosong('Masukkan nilai baru: ')
                    else:
                        # Khusus kolom tagihan: tambah invoice baru atau ubah status
                        print('1. Tambah tagihan baru')
                        print('2. Ubah status tagihan')
                        aksi = input('Pilih (1-2): ')
                        while aksi != '1' and aksi != '2':
                            print('Pilih 1 atau 2.')
                            aksi = input('Pilih (1-2): ')
                        if aksi == '2' and len(daftar_tagihan) == 0:
                            print('Tenant ini belum punya tagihan, jadi diarahkan ke tambah tagihan.')
                            aksi = '1'

                        if aksi == '1':
                            tagihan_baru = input_tagihan_baru()
                        else:
                            # Cari index invoice di list tagihan tenant ini
                            index_tagihan = -1
                            while index_tagihan == -1:
                                no_invoice = input('No Invoice yang diubah: ').upper()
                                for i in range(len(daftar_tagihan)):
                                    if daftar_tagihan[i]['no_invoice'] == no_invoice:
                                        index_tagihan = i
                                if index_tagihan == -1:
                                    print('No Invoice tidak ada di tenant ini.')
                            status_baru = input_status()

                    # Konfirmasi, baru data benar-benar diubah
                    ubah = input_ya_tidak('Ubah data? (y/n): ')
                    if ubah == 'y':
                        if kolom != 'tagihan':
                            data_tenant[tenant_id][kolom] = nilai_baru
                        elif aksi == '1':
                            daftar_tagihan.append(tagihan_baru)
                        else:
                            daftar_tagihan[index_tagihan]['status'] = status_baru
                        print('Data berhasil diubah')
                    else:
                        print('Data batal diubah')
                else:
                    print('Data batal diubah')
        elif pilihan == '2':
            break
        else:
            print('Pilihan yang Anda masukkan tidak valid')


# ---------- MENU DELETE ----------
def menu_delete():
    while True:
        print('\n=== Menu Hapus Data ===')
        print('1. Hapus data tenant')
        print('2. Kembali ke menu utama')
        pilihan = input('Pilih menu (1-2): ')

        if pilihan == '1':
            tenant_id = input_tenant_id('Masukkan Tenant ID: ')  # fitur tambahan 1
            if tenant_id not in data_tenant:
                print('Data yang Anda cari tidak ada')
            else:
                # fitur tambahan 4: tampilkan data + peringatan tunggakan sebelum konfirmasi
                tampil_detail_tenant(tenant_id)
                tunggakan = hitung_belum_lunas(data_tenant[tenant_id]['tagihan'])
                if tunggakan > 0:
                    print('PERINGATAN: tenant ini masih punya tunggakan Rp {}.'.format(tunggakan))
                hapus = input_ya_tidak('Hapus data? (y/n): ')
                if hapus == 'y':
                    del data_tenant[tenant_id]
                    print('Data berhasil dihapus')
                else:
                    print('Data batal dihapus')
        elif pilihan == '2':
            break
        else:
            print('Pilihan yang Anda masukkan tidak valid')


# ---------- MENU UTAMA ----------
def menu_utama():
    while True:
        print('\n===== MONITORING TAGIHAN TENANT =====')
        print('1. Tampilkan data (Read)')
        print('2. Tambah data (Create)')
        print('3. Ubah data (Update)')
        print('4. Hapus data (Delete)')
        print('5. Keluar')
        pilihan = input('Pilih menu (1-5): ')

        if pilihan == '1':
            menu_read()
        elif pilihan == '2':
            menu_create()
        elif pilihan == '3':
            menu_update()
        elif pilihan == '4':
            menu_delete()
        elif pilihan == '5':
            print('Terima kasih, program selesai.')
            break
        else:
            print('Pilihan yang Anda masukkan tidak valid')


# Program mulai dari sini
menu_utama()

import streamlit as st
import requests
import csv
import urllib.parse

# --- 1. CONFIGURAZIONE INTERFACCIA COMPATTA E FLUIDA ---
st.set_page_config(page_title="CRM BOARD - A Casa di Amici 2026", layout="wide", page_icon="🏨")

st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
    .metric-box { background-color: #ffffff; border: 1px solid #cbd5e0; padding: 12px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .card-ospite { background-color: #ffffff !important; border: 1px solid #cbd5e0 !important; padding: 16px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 8px rgba(148, 120, 80, 0.04); width: 100% !important; display: block !important; }
    .badge { padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; }
    .badge-verde { background-color: #e6fffa !important; color: #008767 !important; border: 1px solid #b2f5ea !important; }
    .badge-giallo { background-color: #fefcbf !important; color: #b7791f !important; border: 1px solid #faf089 !important; }
    .badge-rosso { background-color: #fed7d7 !important; color: #c53030 !important; border: 1px solid #feb2b2 !important; }
    .badge-grigio { background-color: #edf2f7 !important; color: #4a5568 !important; border: 1px solid #e2e8f0 !important; }
    .linea-dato { display: inline-block; margin-right: 18px; font-size: 14px; white-space: nowrap !important; }
    .dato-evidenziato { color: #1a202c !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 0px; padding-bottom: 0px;">
    <img src="https://githubusercontent.com" style="max-width: 240px; height: auto; margin-bottom: 5px;" alt="Logo">
    <h1 style="margin: 0; padding: 0; color: #1a202c; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 26px;">A Casa di Amici — Dashboard Direzionale</h1>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

CSV_URL = "https://githubusercontent.com"

def correggi_email(email_grezza):
    em = email_grezza.strip().lower()
    if not em or em == "nd": return "nd"
    sub = {"@gmal.com": "@gmail.com", "@gmaill.com": "@gmail.com", "@libero.it": "@libero.it", "@alice.it": "@alice.it", "@hotmal.com": "@hotmail.com"}
    for k, v in sub.items():
        if em.endswith(k): em = em.replace(k, v)
    return em

def genera_messaggi_programmati(nome, alloggio, data_arr):
    al = alloggio if alloggio.lower() != "nd" else "vostro alloggio"
    w = f"Gentile {nome},\n\nSiamo felici di confermare il tuo soggiorno nel {al} dal {data_arr}. Prenotazione sulla parola: zero caparre, saldi alla reception! Ricorda di proteggere il viaggio con Care4UHotel ed evita la nostra blacklist No-Show. Se arrivi in treno/aereo/bus, la biancheria è gratis!"
    c = f"Ciao {nome}! Ti aspettiamo oggi a Torre Pali. Il {al} è pronto. Ci trovi alla reception per il check-in e il saldo al bancone. Buon viaggio!"
    o = f"Grazie {nome}! Speriamo che il soggiorno nel {al} sia stato splendido. Per la prossima volta potrai prenotare direttamente sul nostro sito usando il tuo codice sconto dedicato!"
    return w, c, o
try:
    risposta = requests.get(CSV_URL)
    if risposta.status_code == 200:
        linee = [l for l in risposta.text.splitlines() if l.strip()]
        if len(linee) > 1:
            lettore = csv.reader(linee)
            next(lettore)
            righe = list(lettore)
            
            tot_fatturato, pratiche_attive = 0.0, 0
            for p in righe:
                if len(p) < 23: continue
                st_p = p[21].strip().lower()
                if "conferma" in st_p or "corso" in st_p or "arrivato" in st_p:
                    pratiche_attive += 1
                    try: tot_fatturato += float(p[16].strip().replace(",", "."))
                    except ValueError: pass
            
            c_m1, c_m2 = st.columns(2)
            with c_m1: st.markdown(f'<div class="metric-box"><span style="font-size:13px; color:#718096; font-weight:600;">💰 FATTURATO CONSOLIDATO</span><br><span style="font-size:22px; font-weight:800; color:#2f855a;">€ {tot_fatturato:,.2f}</span></div>', unsafe_allow_html=True)
            with c_m2: st.markdown(f'<div class="metric-box"><span style="font-size:13px; color:#718096; font-weight:600;">📈 PRATICHE ATTIVE</span><br><span style="font-size:22px; font-weight:800; color:#4c51bf;">{pratiche_attive} CONTATTI DIRETTI</span></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            ricerca = st.text_input("✍ Cerca per nome, e-mail o note interne:", placeholder="Digita per filtrare i record...").strip().lower()
            
            for p in reversed(righe):
                if len(p) < 23: continue
                id_p, d_c, o_c, l_t, cognome, nome, arr, part, allog = p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]
                o_tot, min_n, ad, bam, mail_grezza, port, char, tariff, ext, t_tar, s_sal, t_sog, stato, note = p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18], p[19], p[20], p[21], p[22]
                
                mail = correggi_email(mail_grezza)
                nome_completo = f"{cognome} {nome}".replace("nd ", "").strip() if f"{cognome} {nome}".strip() != "nd nd" else "Ospite"
                allog_v = allog if allog.lower() != "nd" else "Da assegnare"
                tariff_v = tariff if tariff.lower() != "nd" else "0.00"
                
                tel_v = "nd"
                if "tel:" in note.lower():
                    try: tel_v = note.lower().split("tel:")[1].strip().split(" ")[0].strip()
                    except: pass
                
                if ricerca and ricerca not in f"{nome_completo} {port} {allog_v} {note} {mail} {id_p}".lower(): continue
                
                st_l = stato.lower()
                c_badge, v_badge = ("badge-verde", "Confermata / In Corso") if "conferma" in st_l or "corso" in st_l or "arrivato" in st_l else (("badge-giallo", "Lista d'attesa") if "attesa" in st_l or "sospeso" in st_l else (("badge-grigio", "Non Contattabile") if "non contattabile" in st_l else ("badge-rosso", "Richiesta Scaduta")))
                
                st.markdown(f"""
                <div class="card-ospite">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #edf2f7; padding-bottom: 6px;">
                        <span style="font-size: 16px; font-weight: 800;">#{id_p} | {nome_completo}</span>
                        <span class="badge {c_badge}">{v_badge}</span>
                    </div>
                    <div style="margin-bottom: 6px;">
                        <span class="linea-dato">📅 Soggiorno: <span class="dato-evidenziato">{arr} ➔ {part}</span></span>
                        <span class="linea-dato">🏠 Unità: <span class="dato-evidenziato" style="color:#4c51bf;">{allog_v}</span></span>
                        <span class="linea-dato">💶 Tariffa: <span class="dato-evidenziato" style="color:#2f855a;">€ {tariff_v}</span></span>
                        <span class="linea-dato">🌐 Canale: <span class="dato-evidenziato">{port}</span></span>
                    </div>
                    <div style="font-size: 13px; color: #718096; margin-bottom: 8px;">
                        👥 Ospiti: {o_tot} ({ad} Ad. + {bam} Bamb.) | 📧 E-mail: {mail} | ⏱ Lead Time: {l_t} gg
                    </div>
                    <div style="font-size: 13px; color: #4a5568; background-color: #f7fafc; padding: 8px; border-radius: 6px; border-left: 3px solid #cbd5e0;">
                        📌 <b>NOTE:</b> {note} <span style="float: right; font-size: 11px; color: #a0aec0;">Ricevuto: {d_c} alle {o_c}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if "badge-verde" in c_badge:
                    m_welcome, m_checkin, m_checkout = genera_messaggi_programmati(nome_completo, allog_v, arr)
                    with st.expander(f"✉️ Sistema Messaggi Omnicanale per #{id_p}"):
                        canale = st.radio("Invia tramite:", ["E-mail ufficiale", "WhatsApp Direct"], key=f"chan_{id_p}", horizontal=True)
                        if canale == "E-mail ufficiale":
                            st.text_area("🎉 1. Benvenuto", value=m_welcome, height=70, key=f"w_{id_p}")
                            st.text_area("🏠 2. Check-in", value=m_checkin, height=60, key=f"c_{id_p}")
                            st.text_area("⭐ 3. Grazie", value=m_checkout, height=60, key=f"o_{id_p}")
                        else:
                            tel_clean = "".join([c for c in tel_v if c.isdigit()])
                            if tel_clean and not tel_clean.startswith("39") and len(tel_clean) == 10: tel_clean = "39" + tel_clean
                            w_enc = urllib.parse.quote(m_welcome)
                            c_enc = urllib.parse.quote(m_checkin)
                            o_enc = urllib.parse.quote(m_checkout)
                            if tel_clean:
                                st.markdown(f'<a href="https://wa.me{tel_clean}?text={w_enc}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:600; cursor:pointer; margin-bottom:5px;">🎉 Invia Benvenuto su WA</button></a>', unsafe_allow_html=True)
                                st.markdown(f'<a href="https://wa.me{tel_clean}?text={c_enc}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:600; cursor:pointer; margin-bottom:5px;">🏠 Invia Check-in su WA</button></a>', unsafe_allow_html=True)
                                st.markdown(f'<a href="https://wa.me{tel_clean}?text={o_enc}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:4px; font-weight:600; cursor:pointer;">⭐ Invia Grazie su WA</button></a>', unsafe_allow_html=True)
                            else: st.warning("⚠️ Inserire il telefono nelle note (es. tel: 3491234567) per sbloccare WhatsApp.")
        else: st.info("📂 Database vuoto su GitHub.")
    else: st.error("🛑 Errore di connessione a GitHub.")
except Exception as e: st.error(f"🛑 Errore: {e}")

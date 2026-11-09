"""
Script using standard library `csv` module to append high-quality Hinglish,
Devanagari Hindi, and Indian English scam examples to scam_dataset.csv.
"""

import csv

dataset_path = "scam_dataset.csv"

# Read existing dataset to get max ID and count stats
existing_rows = []
max_id = 0

with open(dataset_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_rows.append(row)
        try:
            row_id = int(row['id'])
            if row_id > max_id:
                max_id = row_id
        except ValueError:
            pass

start_id = max_id + 1

new_examples = [
    # --- UPI FRAUD ---
    ("Bhai galti se aapke PhonePe pe ₹5000 chala gaya h. Kripya refund kar do ye QR scan karke PIN daalo.", "hi_roman", "1", "upi_fraud", "upi_wrong_transfer_qr_pin", "curated_india_scam"),
    ("Sir GooglePay bonus claim karne ke liye is link pe click karein aur UPI PIN enter karein: gpay-rewards.in/claim", "hi_roman", "1", "upi_fraud", "upi_pin_for_receiving_money", "curated_india_scam"),
    ("Paytm Cash cashback of Rs 2000 approved! Enter your UPI PIN in Paytm app to receive cash directly.", "en", "1", "upi_fraud", "upi_pin_for_cashback", "curated_india_scam"),
    ("आपके Google Pay खाते में ₹3500 का रिवॉर्ड जमा किया गया है। क्लेम करने के लिए पिन दर्ज करें।", "hi", "1", "upi_fraud", "upi_devanagari_reward", "curated_india_scam"),
    ("Aapko ₹15,000 Paytm lottery ka prize mila h. Receive button dabayein aur apna 4 digit UPI PIN submit karein.", "hi_roman", "1", "upi_fraud", "upi_lottery_claim", "curated_india_scam"),
    ("Sir, main army officer Bol raha hu. Maine aapka OLX item pasand kiya h. Payment ke liye QR code scan karo.", "hi_roman", "1", "upi_fraud", "olx_army_officer_qr_scam", "curated_india_scam"),
    ("Urgent: Your PhonePe wallet cashback Rs 1499 is pending. Click link to receive in bank account.", "en", "1", "upi_fraud", "upi_wallet_cashback", "curated_india_scam"),
    ("Sir galti se 2500 Rs aapko bhej diye text msg dekh lo. Mujhe hospital bill bharna hai wapas gpay kar do.", "hi_roman", "1", "upi_fraud", "fake_hospital_emergency_upi", "curated_india_scam"),
    ("आपके खाते में गलती से ₹4,999 ट्रांसफर हो गए हैं। कृपया दिए गए UPI QR पर वापस भेजें।", "hi", "1", "upi_fraud", "upi_devanagari_wrong_transfer", "curated_india_scam"),
    ("PhonePe Merchant: Congratulations! You received Rs 5000 Scratch Card. Scan QR code to accept.", "en", "1", "upi_fraud", "fake_scratch_card", "curated_india_scam"),

    # --- FAKE JOB ---
    ("Part time online job! Earn Rs 2000-5000 daily by liking YouTube videos. Contact Telegram @job_helper_india", "hi_roman", "1", "fake_job", "youtube_like_telegram_job", "curated_india_scam"),
    ("Work from home job opportunity in Amazon India. Daily payout Rs 3500. Registration fee Rs 499 required.", "en", "1", "fake_job", "upfront_reg_fee", "curated_india_scam"),
    ("Aapka resume shortlisted hua h Indigo Airlines main ground staff post ke liye. Training fee 1200 Rs pay karein.", "hi_roman", "1", "fake_job", "airline_job_scam", "curated_india_scam"),
    ("घर बैठे रोजाना 2000 से 4000 रुपये कमाएं! डेटा एंट्री जॉब। रजिस्ट्रेशन फीस ₹350 जमा करें।", "hi", "1", "fake_job", "data_entry_devanagari", "curated_india_scam"),
    ("Dear candidate, your profile is selected for Govt Typing job. Pay security deposit Rs 999 to start.", "en", "1", "fake_job", "typing_job_security_deposit", "curated_india_scam"),
    ("Google India part-time work from home! Task complete karo aur per task Rs 500 pao. Telegram join karein.", "hi_roman", "1", "fake_job", "google_fake_task_job", "curated_india_scam"),
    ("Captch filling work available. No skill required. Weekly salary Rs 15000. Laptop kit charge Rs 750 upfront.", "en", "1", "fake_job", "captcha_job_laptop_fee", "curated_india_scam"),
    ("Aapko Flipkart merchant assistant post mili h. Daily payment ₹2500. WhatsApp us immediately.", "hi_roman", "1", "fake_job", "flipkart_assistant_scam", "curated_india_scam"),
    ("वर्क फ्रॉम होम! केवल 2 घंटे काम करके पाएं ₹30,000 महीना। अभी टेलीग्राम ग्रुप जॉइन करें।", "hi", "1", "fake_job", "telegram_task_devanagari", "curated_india_scam"),
    ("Selected for Wipro Remote Software Tester. Pay laptop dispatch fee Rs 1500 to receive company laptop.", "en", "1", "fake_job", "wipro_laptop_fee_scam", "curated_india_scam"),

    # --- LOAN APP SCAM ---
    ("Instant Loan approved Rs 1,00,000 in 5 mins without CIBIL score! Pay processing fee Rs 999 to get disbursal.", "en", "1", "loan_app_scam", "no_cibil_processing_fee", "curated_india_scam"),
    ("Aapka 50,000 ka Instant Cash Loan pass ho gaya hai bina kisi paper ke. Abhi link pe click karein: fastloan.apk", "hi_roman", "1", "loan_app_scam", "instant_loan_apk", "curated_india_scam"),
    ("बिना किसी डॉक्यूमेंट के ₹2,00,000 का पर्सनल लोन स्वीकृत। फाइल चार्ज ₹1499 भुगतान करें।", "hi", "1", "loan_app_scam", "loan_devanagari_file_charge", "curated_india_scam"),
    ("Urgent: Dhani Loan app approved Rs 75000 for your mobile number. Pay Insurance Fee Rs 1200 first.", "en", "1", "loan_app_scam", "fake_dhani_insurance_fee", "curated_india_scam"),
    ("Bhai bina kisi guarantor ke 3 lakh ka loan 2% interest pe chahiye toh abhi WhatsApp karo is number par.", "hi_roman", "1", "loan_app_scam", "low_interest_whatsapp_loan", "curated_india_scam"),
    ("Your Mudra Yojana Loan of Rs 5,00,000 is approved by Govt. Deposit approval tax Rs 2999.", "en", "1", "loan_app_scam", "fake_govt_mudra_loan", "curated_india_scam"),
    ("PaisaBazaar Alert: Special pre-approved credit line Rs 80,000 available. Download app from unverified link.", "en", "1", "loan_app_scam", "unverified_apk_loan", "curated_india_scam"),
    ("5 मिनट में लोन प्राप्त करें! कोई सिबिल स्कोर की जरूरत नहीं। अभी ऐप डाउनलोड करें।", "hi", "1", "loan_app_scam", "instant_loan_devanagari", "curated_india_scam"),
    ("Aapka loan overdue ho gaya h. Agar 1 ghante me ₹5000 nahi bhara toh aapke contacts ko photo leak kar dunga.", "hi_roman", "1", "loan_app_scam", "blackmail_loan_app", "curated_india_scam"),

    # --- FAKE CUSTOMER CARE ---
    ("SBI Customer Care helpline number changed! For quick issue resolution call 9876543210 immediately.", "en", "1", "fake_customer_care", "fake_bank_helpline_search", "curated_india_scam"),
    ("Aapka Courier package hold par hai wrong address ki wajah se. Update address & pay ₹5 fee: delivery-fix.com", "hi_roman", "1", "fake_customer_care", "courier_address_update_scam", "curated_india_scam"),
    ("Swiggy Refund Support: Aapka ₹450 refund pending hai. Support agent se baat karne ke liye Call 9123456789.", "hi_roman", "1", "fake_customer_care", "swiggy_refund_fake_support", "curated_india_scam"),
    ("बिजली बिल अपडेट नहीं होने के कारण आज रात 9 बजे आपकी बिजली काट दी जाएगी। कस्टमर केयर से संपर्क करें।", "hi", "1", "fake_customer_care", "electricity_bill_devanagari", "curated_india_scam"),
    ("Airtel 5G SIM upgrade alert! Your SIM will be deactivated today. Call officer at 9988776655 to keep active.", "en", "1", "fake_customer_care", "sim_deactivation_call", "curated_india_scam"),
    ("Amazon India refund section: Your returned item refund Rs 3490 failed. Call customer executive 8877665544.", "en", "1", "fake_customer_care", "amazon_refund_fake_num", "curated_india_scam"),
    ("Zomato Support Team: Aapka bill amount double kat gaya h. Refund ke liye AnyDesk app install karke code batayein.", "hi_roman", "1", "fake_customer_care", "anydesk_remote_desktop_scam", "curated_india_scam"),
    ("Indane Gas Booking customer service number 9811223344. Call here for urgent cylinder delivery.", "en", "1", "fake_customer_care", "gas_agency_fake_num", "curated_india_scam"),

    # --- PHISHING ---
    ("Dear HDFC customer, your netbanking will be suspended today. Update your PAN card details immediately: hdfc-pan-verify.info", "en", "1", "phishing", "bank_pan_update_phishing", "curated_india_scam"),
    ("Aapka SBI yono account block kar diya gaya h. Unblock karne ke liye is link pe login karein: sbi-yono-update.biz", "hi_roman", "1", "phishing", "sbi_yono_block_phishing", "curated_india_scam"),
    ("Dear Consumer, Electricity power connection will be disconnected tonight at 9:30 PM from discom office. Call officer 9123412345", "en", "1", "phishing", "electricity_discom_phishing", "curated_india_scam"),
    ("प्रिय ग्राहक, आपका पीएनबी बैंक खाता ब्लॉक हो गया है। केवाईसी अपडेट करने के लिए तुरंत लिंक पर क्लिक करें।", "hi", "1", "phishing", "pnb_kyc_devanagari", "curated_india_scam"),
    ("Jio User Special Offer: Get 84 Days 2GB/day Free Data! Activate now before offer ends: jio-free-5g.top", "hi_roman", "1", "phishing", "jio_free_recharge_phishing", "curated_india_scam"),
    ("Income Tax Refund of Rs 15,400 has been approved for your account. Verify bank account to receive refund: it-refund-portal.net", "en", "1", "phishing", "income_tax_refund_phishing", "curated_india_scam"),
    ("Aapka EPFO pension account hold par h. Aadhaar OTP share karke verify karein.", "hi_roman", "1", "phishing", "epfo_pension_phishing", "curated_india_scam"),
    ("Challan Alert: Traffic fine Rs 1000 generated for your vehicle. Pay online within 24 hours to avoid court notice: e-challan-pay.co", "en", "1", "phishing", "fake_traffic_challan_link", "curated_india_scam"),
    ("PM Kisan Samman Nidhi Yojana: ₹2000 ki kist aapke khate me bheji gayi h. Status check karein: pm-kisan-gov.site", "hi_roman", "1", "phishing", "pm_kisan_scheme_scam", "curated_india_scam"),
    ("आपका व्हाट्सएप ब्लॉक कर दिया जाएगा। सुरक्षा के लिए भेजा गया 6 अंकों का कोड तुरंत दर्ज करें।", "hi", "1", "phishing", "whatsapp_otp_devanagari", "curated_india_scam"),

    # --- LOTTERY SCAM ---
    ("KBC Lucky Draw 2026: Aapka mobile number 25 Lakh INR ki lottery jeet chuka h. Call KBC Manager Rana Pratap on WhatsApp.", "hi_roman", "1", "lottery_scam", "kbc_25_lakh_whatsapp", "curated_india_scam"),
    ("Congratulations! You have won Tata Safari SUV in Naaptol lucky winner contest. Pay registration tax Rs 4500.", "en", "1", "lottery_scam", "naaptol_car_lottery", "curated_india_scam"),
    ("बधाई हो! आपने कौन बनेगा करोड़पति में ₹25,00,000 की लॉटरी जीती है। दावा करने के लिए बैंक विवरण भेजें।", "hi", "1", "lottery_scam", "kbc_devanagari_lottery", "curated_india_scam"),
    ("Shoppers Stop Diwali Bonus Offer: Claim your free iPhone 15 Pro Max now! Pay delivery charge Rs 299: free-gift-claim.xyz", "en", "1", "lottery_scam", "free_iphone_delivery_charge", "curated_india_scam"),
    ("Aapko Jio 10th Anniversary Spin & Win me 1 Lakh Rs cash prize mila hai. Claim karne ke liye 5 WhatsApp groups me share karein.", "hi_roman", "1", "lottery_scam", "spin_win_share_whatsapp", "curated_india_scam"),
    ("Dear Lucky Winner, your SIM card won Rs 12,00,000 in All India Sim Card Lucky Draw. Call 9988112233.", "en", "1", "lottery_scam", "sim_card_lucky_draw", "curated_india_scam"),

    # --- INVESTMENT SCAM ---
    ("Guaranteed 5% daily return on Crypto Trading! Join our VIP Telegram channel for free trading signals: t.me/crypto_king_india", "en", "1", "investment_scam", "crypto_daily_guaranteed_return", "curated_india_scam"),
    ("Stock Market Option Trading Expert: Double your money in 3 days with zero risk! WhatsApp 9876500000 for multibagger tips.", "en", "1", "investment_scam", "double_money_stock_tips", "curated_india_scam"),
    ("Aap 5000 Rs invest karein aur har roz 500 Rs fixed profit paayein. Company Govt registered hai 100% safe.", "hi_roman", "1", "investment_scam", "daily_fixed_profit_scam", "curated_india_scam"),
    ("शेयर बाजार में 100% गारंटीड मुनाफा! 10,000 रुपये लगाएं और 1 महीने में 50,000 रुपये पाएं।", "hi", "1", "investment_scam", "investment_devanagari_guaranteed", "curated_india_scam"),
    ("Pre-IPO Allotment Offer: Get Tata Technologies shares at 50% discount before listing. Deposit funds in private account.", "en", "1", "investment_scam", "fake_pre_ipo_discount", "curated_india_scam"),
    ("Gold Investment Scheme: Deposit Rs 1000 monthly and get 300% bonus after 6 months. Approved by SEBI.", "en", "1", "investment_scam", "fake_gold_scheme_sebi", "curated_india_scam"),

    # --- LEGITIMATE (EN / HI / HI_ROMAN) ---
    ("Dear Customer, Rs. 1450.00 debited from a/c XX4019 on 12-AUG-26 at AMZN Mktp. Avail Bal: Rs. 12,300.00. - HDFC Bank", "en", "0", "legitimate", "real_bank_debit_alert", "curated_india_legit"),
    ("Aapka OTP for Swiggy order is 849201. Do not share this OTP with anyone, including Swiggy delivery executive.", "hi_roman", "0", "legitimate", "real_otp_warning", "curated_india_legit"),
    ("Dear SBI User, your account statement for July 2026 is generated. Download from official YONO app.", "en", "0", "legitimate", "real_bank_statement_notice", "curated_india_legit"),
    ("Bhai shaam ko 7 baje chai pe milte hain, wo office waala document leke aana.", "hi_roman", "0", "legitimate", "real_personal_chat", "curated_india_legit"),
    ("प्रिय ग्राहक, आपका बिजली बिल ₹850 सफलतापूर्वक प्राप्त हुआ है। धन्यवाद - बीएसईएस", "hi", "0", "legitimate", "real_utility_payment_receipt_devanagari", "curated_india_legit"),
    ("Your Zomato order has been picked up by delivery partner Ramesh. Track live location in app.", "en", "0", "legitimate", "real_delivery_tracking", "curated_india_legit"),
    ("Aapka Amazon package aaj deliver hone wala h. Delivery pin: 4920.", "hi_roman", "0", "legitimate", "real_delivery_pin", "curated_india_legit"),
    ("Your Jio plan of Rs 299 is expiring in 2 days. Recharge via MyJio app or jio.com to enjoy uninterrupted service.", "en", "0", "legitimate", "real_recharge_reminder", "curated_india_legit"),
    ("Mummy ne pucha ki aap ghar kab tak aaoge, khana garam karke rakh de.", "hi_roman", "0", "legitimate", "real_family_message", "curated_india_legit"),
    ("Dear Student, your semester exam hall ticket is available on official university portal univ.ac.in", "en", "0", "legitimate", "real_university_notice", "curated_india_legit"),
    ("आपका आईसीआईसीआई बैंक खाते का 459032 ओटीपी है। इसे किसी के साथ साझा न करें।", "hi", "0", "legitimate", "real_otp_devanagari", "curated_india_legit"),
    ("Appointment confirmed with Dr. Sharma on 14-Aug at 11:30 AM at Max Healthcare Hospital.", "en", "0", "legitimate", "real_doctor_appointment", "curated_india_legit"),
    ("Bhai wo room ki chaabi table pe rakhi hai, lock karke nikalna.", "hi_roman", "0", "legitimate", "real_friends_chat", "curated_india_legit"),
    ("Your Uber ride is arriving in 3 mins. Driver name: Suresh, Car: Swift Dzire MH02AB1234.", "en", "0", "legitimate", "real_uber_ride_alert", "curated_india_legit"),
]

fieldnames = ["id", "text", "language", "is_scam", "category", "confidence_note", "source"]

with open(dataset_path, mode='a', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    for i, (text, lang, is_scam, cat, note, src) in enumerate(new_examples, start=start_id):
        writer.writerow({
            "id": str(i),
            "text": text,
            "language": lang,
            "is_scam": is_scam,
            "category": cat,
            "confidence_note": note,
            "source": src
        })

print(f"Successfully added {len(new_examples)} new examples using standard library csv! New max ID: {start_id + len(new_examples) - 1}")

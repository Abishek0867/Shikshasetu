"""Translation table (English, Hindi, Tamil) for all UI labels, statuses and chatbot replies."""
T = {
 "en": dict(
   app="ShikshaSetu", tagline="All your ST scholarships in one place",
   login="Log in", logout="Log out",
   apaar="APAAR ID", otp="OTP", hello="Welcome", received="Total received",
   pending="Pending actions", none="Nothing pending",
   my_apps="My applications", schemes="Scholarship schemes", apply="Apply",
   consent="I consent to fetching my records from DigiLocker, UIDAI and e-District.",
   docs="Document wallet (DigiLocker)", sync="Fetch from DigiLocker",
   family="Family applications", notif="Notifications",
   chat="JAGO assistant", chat_ph="Ask about status, payment, documents, eligibility",
   send="Send", details="Details", resubmit="Resubmit",
   eligible="Matches your level", steps=["Submitted", "Verified", "Sanctioned", "Paid"],
   hint="Demo OTP: 123456",
   # Dashboard
   dashboard="Dashboard", profile="Personal Details", doc_wallet="Document Wallet",
   notice_board="Notice Board", logout_btn="Logout", student_portal="Student Portal",
   officer_portal="Officer Portal", scheme_officer="Scheme Officer View",
   review="Review & Sanctions", analytics="Coverage Gap Analytics", rbac="RBAC Admin",
   student_view="Student View",
   # Bank & DBT
   dbt_bank="Direct Benefit Transfer (DBT) Linked Bank Account",
   total_grant="Total Scholarship Grant Received",
   live_balance="Live Wallet Balance",
   aadhaar_seeded="Aadhaar Seeded",
   # Application status steps
   submitted="Submitted", verified="Verified", sanctioned="Sanctioned", paid="Paid",
   # Schemes
   pre_matric="Pre-Matric", post_matric="Post-Matric",
   top_class="Top Class", nfst="NFST Fellowship", nos="NOS Overseas",
   # Actions
   upload="Upload Document", verify_doc="Verify Document",
   apply_now="Apply Now", view_status="View Status",
   track="Track Application", download="Download",
   # Registration
   register="New Registration", name="Full Name", state="State", district="District",
   dob="Date of Birth", category="Category", income="Annual Family Income",
   level="Study Level", institute="Institute Name",
   bank="Bank Name", account="Account Number", ifsc="IFSC Code",
   submit="Submit", already_user="Already registered?",
   # Login page labels
   user_id="User ID (APAAR Number)", password="Password / OTP",
   captcha="Captcha", login_btn="Login",
   officer_login="Officer Login", new_user="New User? Register",
   # Notifications
   no_notif="No notifications yet.",
   # Officer portal
   approve="Approve", reject="Reject", sanction="Sanction",
   disburse="Disburse", bulk_sanction="Bulk Sanction DBT",
   pending_review="Pending Review", all_apps="All Applications",
   announce="Announce New Scheme",
   # Wallet
   wallet_empty="Your wallet is empty. Fetch documents from DigiLocker.",
   fetch_docs="Fetch from DigiLocker",
   # Misc
   search="Search", filter="Filter", export="Export",
   close="Close", back="Back", next="Next", save="Save",
   loading="Loading...", success="Success!", error="Error!",
 ),
 "hi": dict(
   app="शिक्षासेतु", tagline="सभी ST छात्रवृत्तियाँ एक ही जगह",
   login="लॉगिन", logout="लॉगआउट",
   apaar="APAAR आईडी", otp="ओटीपी", hello="स्वागत है", received="कुल प्राप्त राशि",
   pending="लंबित कार्य", none="कोई कार्य लंबित नहीं",
   my_apps="मेरे आवेदन", schemes="छात्रवृत्ति योजनाएँ", apply="आवेदन करें",
   consent="मैं DigiLocker, UIDAI और e-District से अपने रिकॉर्ड लेने की सहमति देता/देती हूँ।",
   docs="दस्तावेज़ वॉलेट (DigiLocker)", sync="DigiLocker से लाएँ",
   family="परिवार के आवेदन", notif="सूचनाएँ",
   chat="JAGO सहायक", chat_ph="स्थिति, भुगतान, दस्तावेज़ या पात्रता के बारे में पूछें",
   send="भेजें", details="विवरण", resubmit="दोबारा जमा करें",
   eligible="आपके स्तर के अनुसार", steps=["जमा", "सत्यापित", "स्वीकृत", "भुगतान"],
   hint="डेमो OTP: 123456",
   # Dashboard
   dashboard="डैशबोर्ड", profile="व्यक्तिगत विवरण", doc_wallet="दस्तावेज़ वॉलेट",
   notice_board="सूचना पटल", logout_btn="लॉगआउट", student_portal="छात्र पोर्टल",
   officer_portal="अधिकारी पोर्टल", scheme_officer="योजना अधिकारी दृश्य",
   review="समीक्षा और स्वीकृति", analytics="कवरेज विश्लेषण", rbac="RBAC एडमिन",
   student_view="छात्र दृश्य",
   # Bank & DBT
   dbt_bank="प्रत्यक्ष लाभ अंतरण (DBT) से जुड़ा बैंक खाता",
   total_grant="कुल छात्रवृत्ति अनुदान प्राप्त",
   live_balance="लाइव वॉलेट बैलेंस",
   aadhaar_seeded="आधार सीडेड",
   # Application status steps
   submitted="जमा किया गया", verified="सत्यापित", sanctioned="स्वीकृत", paid="भुगतान",
   # Schemes
   pre_matric="प्री-मैट्रिक", post_matric="पोस्ट-मैट्रिक",
   top_class="टॉप क्लास", nfst="NFST फेलोशिप", nos="NOS विदेश",
   # Actions
   upload="दस्तावेज़ अपलोड करें", verify_doc="दस्तावेज़ सत्यापित करें",
   apply_now="अभी आवेदन करें", view_status="स्थिति देखें",
   track="आवेदन ट्रैक करें", download="डाउनलोड",
   # Registration
   register="नया पंजीकरण", name="पूरा नाम", state="राज्य", district="जिला",
   dob="जन्म तिथि", category="श्रेणी", income="वार्षिक पारिवारिक आय",
   level="अध्ययन स्तर", institute="संस्थान का नाम",
   bank="बैंक का नाम", account="खाता संख्या", ifsc="IFSC कोड",
   submit="जमा करें", already_user="पहले से पंजीकृत हैं?",
   # Login page labels
   user_id="यूजर आईडी (APAAR नंबर)", password="पासवर्ड / ओटीपी",
   captcha="कैप्चा", login_btn="लॉगिन करें",
   officer_login="अधिकारी लॉगिन", new_user="नए उपयोगकर्ता? पंजीकरण करें",
   # Notifications
   no_notif="अभी कोई सूचना नहीं।",
   # Officer portal
   approve="स्वीकार करें", reject="अस्वीकार करें", sanction="स्वीकृत करें",
   disburse="वितरित करें", bulk_sanction="थोक DBT स्वीकृति",
   pending_review="समीक्षा के लिए लंबित", all_apps="सभी आवेदन",
   announce="नई योजना की घोषणा करें",
   # Wallet
   wallet_empty="आपका वॉलेट खाली है। DigiLocker से दस्तावेज़ लाएँ।",
   fetch_docs="DigiLocker से लाएँ",
   # Misc
   search="खोजें", filter="फ़िल्टर", export="निर्यात",
   close="बंद करें", back="वापस", next="अगला", save="सहेजें",
   loading="लोड हो रहा है...", success="सफलता!", error="त्रुटि!",
 ),
 "ta": dict(
   app="ஷிக்ஷாசேது", tagline="அனைத்து ST கல்வி உதவித்தொகைகளும் ஒரே இடத்தில்",
   login="உள்நுழை", logout="வெளியேறு",
   apaar="APAAR ஐடி", otp="OTP", hello="வரவேற்கிறோம்", received="பெற்ற மொத்த தொகை",
   pending="நிலுவையில் உள்ளவை", none="நிலுவை எதுவும் இல்லை",
   my_apps="என் விண்ணப்பங்கள்", schemes="உதவித்தொகை திட்டங்கள்", apply="விண்ணப்பிக்க",
   consent="DigiLocker, UIDAI, e-District-இலிருந்து என் பதிவுகளைப் பெற ஒப்புக்கொள்கிறேன்.",
   docs="ஆவண வாலட் (DigiLocker)", sync="DigiLocker-இலிருந்து பெறு",
   family="குடும்ப விண்ணப்பங்கள்", notif="அறிவிப்புகள்",
   chat="JAGO உதவியாளர்", chat_ph="நிலை, பணம், ஆவணங்கள், தகுதி பற்றி கேளுங்கள்",
   send="அனுப்பு", details="விவரங்கள்", resubmit="மீண்டும் சமர்ப்பி",
   eligible="உங்கள் நிலைக்கு பொருந்தும்", steps=["சமர்ப்பிப்பு", "சரிபார்ப்பு", "அனுமதி", "பணம்"],
   hint="டெமோ OTP: 123456",
   # Dashboard
   dashboard="டாஷ்போர்டு", profile="தனிப்பட்ட விவரங்கள்", doc_wallet="ஆவண வாலட்",
   notice_board="அறிவிப்பு பலகை", logout_btn="வெளியேறு", student_portal="மாணவர் போர்டல்",
   officer_portal="அதிகாரி போர்டல்", scheme_officer="திட்ட அதிகாரி பார்வை",
   review="மதிப்பாய்வு & அனுமதி", analytics="கவரேஜ் பகுப்பாய்வு", rbac="RBAC நிர்வாகம்",
   student_view="மாணவர் பார்வை",
   # Bank & DBT
   dbt_bank="நேரடி நலன் பரிமாற்றம் (DBT) இணைக்கப்பட்ட வங்கி கணக்கு",
   total_grant="பெற்ற மொத்த உதவித்தொகை மானியம்",
   live_balance="நேரடி வாலட் இருப்பு",
   aadhaar_seeded="ஆதார் இணைக்கப்பட்டது",
   # Application status steps
   submitted="சமர்ப்பிக்கப்பட்டது", verified="சரிபார்க்கப்பட்டது",
   sanctioned="அனுமதிக்கப்பட்டது", paid="பணம் வழங்கப்பட்டது",
   # Schemes
   pre_matric="முன்-மெட்ரிக்", post_matric="பின்-மெட்ரிக்",
   top_class="டாப் கிளாஸ்", nfst="NFST ஃபெல்லோஷிப்", nos="NOS வெளிநாடு",
   # Actions
   upload="ஆவணம் பதிவேற்று", verify_doc="ஆவணம் சரிபார்",
   apply_now="இப்போது விண்ணப்பிக்கவும்", view_status="நிலையை காண்க",
   track="விண்ணப்பம் கண்காணி", download="பதிவிறக்கம்",
   # Registration
   register="புதிய பதிவு", name="முழு பெயர்", state="மாநிலம்", district="மாவட்டம்",
   dob="பிறந்த தேதி", category="வகை", income="வருடாந்திர குடும்ப வருமானம்",
   level="படிப்பு நிலை", institute="நிறுவனத்தின் பெயர்",
   bank="வங்கியின் பெயர்", account="கணக்கு எண்", ifsc="IFSC குறியீடு",
   submit="சமர்ப்பி", already_user="ஏற்கனவே பதிவு செய்தீர்களா?",
   # Login page labels
   user_id="பயனர் ஐடி (APAAR எண்)", password="கடவுச்சொல் / OTP",
   captcha="கேப்சா", login_btn="உள்நுழைக",
   officer_login="அதிகாரி உள்நுழைவு", new_user="புதிய பயனர்? பதிவு செய்க",
   # Notifications
   no_notif="இன்னும் அறிவிப்புகள் இல்லை.",
   # Officer portal
   approve="அங்கீகரி", reject="நிராகரி", sanction="அனுமதி",
   disburse="வழங்கு", bulk_sanction="மொத்த DBT அனுமதி",
   pending_review="மதிப்பாய்வுக்காக நிலுவை", all_apps="அனைத்து விண்ணப்பங்கள்",
   announce="புதிய திட்டத்தை அறிவி",
   # Wallet
   wallet_empty="உங்கள் வாலட் காலியாக உள்ளது. DigiLocker-இலிருந்து ஆவணங்களைப் பெறுங்கள்.",
   fetch_docs="DigiLocker-இலிருந்து பெறு",
   # Misc
   search="தேடு", filter="வடிகட்டு", export="ஏற்றுமதி",
   close="மூடு", back="திரும்பு", next="அடுத்து", save="சேமி",
   loading="ஏற்றுகிறது...", success="வெற்றி!", error="பிழை!",
 ),
}
STATUS = {
 "en": dict(SUBMITTED="Submitted", UNDER_REVIEW="Under manual review", DEFICIENCY="Correction needed",
            VERIFIED="Verified, awaiting sanction", SANCTIONED="Sanctioned", DISBURSED="Payment released", REJECTED="Rejected"),
 "hi": dict(SUBMITTED="जमा किया गया", UNDER_REVIEW="मैनुअल समीक्षा में", DEFICIENCY="सुधार आवश्यक",
            VERIFIED="सत्यापित, स्वीकृति प्रतीक्षित", SANCTIONED="स्वीकृत", DISBURSED="भुगतान जारी", REJECTED="अस्वीकृत"),
 "ta": dict(SUBMITTED="சமர்ப்பிக்கப்பட்டது", UNDER_REVIEW="கைமுறை மதிப்பாய்வில்", DEFICIENCY="திருத்தம் தேவை",
            VERIFIED="சரிபார்க்கப்பட்டது, அனுமதிக்காக காத்திருப்பு", SANCTIONED="அனுமதிக்கப்பட்டது",
            DISBURSED="பணம் வழங்கப்பட்டது", REJECTED="நிராகரிக்கப்பட்டது"),
}
CHAT = {
 "en": dict(
   noapp="You have no active application yet. Ask 'am I eligible?' to see what you can apply for.", reason="Reason: {r}",
   paid="Rs {amt} was paid on {date} for {scheme} (DBT: {dbt}).", notpaid="Payment for {scheme} is not released yet. Current stage: {status}.",
   docs="Documents in your wallet: {docs}.", nodocs="Your wallet is empty. Tap 'Fetch from DigiLocker' on the dashboard.",
   elig="Based on your study level you can apply for: {schemes}. Only one scholarship is allowed at a time.",
   help="I can help with application status, payments, documents and eligibility. Try: 'What is my status?'"),
 "hi": dict(
   noapp="आपका अभी कोई सक्रिय आवेदन नहीं है। 'क्या मैं पात्र हूँ' पूछें।", reason="कारण: {r}",
   paid="{scheme} के लिए Rs {amt} का भुगतान {date} को हुआ (DBT: {dbt})।", notpaid="{scheme} का भुगतान अभी जारी नहीं हुआ। वर्तमान चरण: {status}।",
   docs="आपके वॉलेट में दस्तावेज़: {docs}।", nodocs="आपका वॉलेट खाली है। डैशबोर्ड पर 'DigiLocker से लाएँ' दबाएँ।",
   elig="आपके स्तर के अनुसार आप इनके लिए आवेदन कर सकते हैं: {schemes}। एक समय में केवल एक छात्रवृत्ति मान्य है।",
   help="मैं आवेदन स्थिति, भुगतान, दस्तावेज़ और पात्रता में मदद कर सकता हूँ।"),
 "ta": dict(
   noapp="உங்களுக்கு இன்னும் செயலில் உள்ள விண்ணப்பம் இல்லை. 'நான் தகுதியா' என்று கேளுங்கள்.", reason="காரணம்: {r}",
   paid="{scheme}-க்கு Rs {amt} {date} அன்று வழங்கப்பட்டது (DBT: {dbt}).", notpaid="{scheme} தொகை இன்னும் வழங்கப்படவில்லை. தற்போதைய நிலை: {status}.",
   docs="உங்கள் வாலட்டில் உள்ள ஆவணங்கள்: {docs}.", nodocs="வாலட் காலியாக உள்ளது. டாஷ்போர்டில் 'DigiLocker-இலிருந்து பெறு' அழுத்தவும்.",
   elig="உங்கள் நிலைக்கு இவற்றுக்கு விண்ணப்பிக்கலாம்: {schemes}. ஒரு நேரத்தில் ஒரு உதவித்தொகை மட்டுமே.",
   help="விண்ணப்ப நிலை, பணம், ஆவணங்கள், தகுதி பற்றி உதவ முடியும்."),
}

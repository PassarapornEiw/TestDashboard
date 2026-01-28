*** Variables ***
# Base URLs - BASE_URL is set dynamically from settings.json via Initialize Browser
${BASE_URL}                          ${EMPTY}    # Set by Initialize Browser from settings.json
${AUTH_PAGE}                         authentication.html
${OTP1_PAGE}                         otp1.html
${SELECT_CARD_PAGE}                  select_credit_card.html
${OFFERING_PROGRAM_PAGE}             offering_program.html
${PROGRAM_DETAILS_PAGE}              program_details.html
${SET_PAYMENT_PAGE}                  set_new_payment.html
${CONDITION_PAGE}                    condition.html
${REGISTRATION_STEPS_PAGE}           registration_steps_info.html
${RISK_QUESTIONNAIRE_PAGE}           risk_questionnaire.html
${E_CONTRACT_PAGE}                   e_contract_and_t_c.html
${OTP_CONFIRMATION_PAGE}             otp_confirmation.html
${SUCCESS_PAGE}                      successful_registered.html
${ACCOUNT_LOCKED_PAGE}               account_locked.html
${SESSION_TIMEOUT_PAGE}              session_timeout.html
${SURVEY_PAGE}                       survey.html

# Test Data
${VALID_OTP}                         123456
${VALID_ID_CARD}                     1-2345-67890-12-3
${VALID_PHONE}                       082-999-9999
${INVALID_ID_CARD}                   123456789
${INVALID_PHONE}                     12345

# Program Types
${PROGRAM_TYPE_DEBT_RE}              debt re
${PROGRAM_TYPE_REWRITE_SETTLEMENT}   rewrite settlement

# Timeouts
${SHORT_TIMEOUT}                     5s
${MEDIUM_TIMEOUT}                    10s
${LONG_TIMEOUT}                      30s

# Expected Text
${EXPECTED_TITLE}                    วางแผนการชำระ
${ERROR_FORMAT_MESSAGE}              คุณกรอกข้อมูลผิดรูปแบบ
${ACCOUNT_LOCKED_MESSAGE}            ระบบถูกล็อกเนื่องจากทำรายการผิดเกินจำนวนครั้งที่กำหนด

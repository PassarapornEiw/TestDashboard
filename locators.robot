*** Variables ***
# Common Locators
${HEADER_TITLE}                      xpath=//div[@class='header-title']
${BACK_BUTTON}                       xpath=//a[contains(@class, 'back-btn')]
${CLOSE_BUTTON}                      xpath=//a[contains(@class, 'close-btn')]
${CONTINUE_BUTTON}                   xpath=//button[contains(@class, 'btn-primary') and contains(text(), 'ดำเนินการต่อ')]

# Authentication Page
${AUTH_ID_CARD_INPUT}                id=idCard
${AUTH_PHONE_INPUT}                  id=phoneNumber
${AUTH_ID_CARD_ERROR}                id=idCardError
${AUTH_PHONE_ERROR}                  id=phoneError
${AUTH_CONTINUE_BUTTON}              id=btnContinue

# Account Locked Page
${LOCK_ICON}                         xpath=//div[contains(@class, 'lock-icon')]
${LOCK_MESSAGE}                      xpath=//div[contains(@class, 'step-description')]
${LOCK_MINUTES}                      id=lockoutMinutes

# OTP1 Page
${OTP1_PHONE_DISPLAY}                id=phoneDisplay
${OTP1_REFERENCE_CODE}               id=referenceCode
${OTP1_INPUT_1}                      id=otp1
${OTP1_INPUT_2}                      id=otp2
${OTP1_INPUT_3}                      id=otp3
${OTP1_INPUT_4}                      id=otp4
${OTP1_INPUT_5}                      id=otp5
${OTP1_INPUT_6}                      id=otp6
${OTP1_RESEND_LINK}                  id=btnResend
${OTP1_CONFIRM_BUTTON}               id=btnConfirm
${OTP1_ERROR}                        id=otpError

# Select Credit Card Page
${CARD_OPTION_1}                     xpath=//input[@name='creditCard' and @value='card1']
${CARD_OPTION_2}                     xpath=//input[@name='creditCard' and @value='card2']
${CARD_OPTION_3}                     xpath=//input[@name='creditCard' and @value='card3']
${CARD_DISABLED}                     xpath=//label[contains(@class, 'disabled')]
${CARD_CONTINUE_BUTTON}              id=btnContinue

# Offering Program Page
${PROGRAM_COUNT}                     id=programCount
${ELIGIBILITY_MESSAGE}               id=eligibilityMessage
${PROGRAM_LIST}                      id=programList
${PROGRAM_RADIO_1}                   xpath=//input[@name='program' and @value='debt-restructuring']
${PROGRAM_RADIO_2}                   xpath=//input[@name='program' and @value='debt-restructuring-discount']
${PROGRAM_CONTINUE_BUTTON}           id=btnContinue

# Program Details Page
${PROGRAM_DETAILS_TITLE}             id=programDetailsTitle
${PROGRAM_INTEREST_RATE}             id=interestRate
${PROGRAM_INSTALLMENTS}              id=installments
${PROGRAM_MONTHLY_PAYMENT}           id=monthlyPayment
${PAYMENT_CONDITIONS_SECTION}        id=paymentConditionsSection
${CONTACT_INFO_SECTION}              id=contactInfoSection
${BTN_INTERESTED}                    id=btnInterested
${BTN_SET_NEW_PAYMENT}               id=btnSetNewPayment

# Set New Payment Page
${PAYMENT_AMOUNT_INPUT}              id=paymentAmount
${CALCULATE_BUTTON}                  id=btnCalculate
${CALCULATION_RESULT}                id=calculationResult
${CALC_INTEREST_RATE}                id=calcInterestRate
${CALC_INSTALLMENTS}                 id=calcInstallments
${CALC_MONTHLY_PAYMENT}              id=calcMonthlyPayment
${PAYMENT_CONTINUE_BUTTON}           id=btnContinue

# Condition Page
${BEFORE_CONDITION}                  id=beforeCondition
${DISCOUNT}                          id=discount
${AFTER_CONDITION}                   id=afterCondition
${ACCEPT_CONDITION_CHECKBOX}         id=acceptCondition
${CONDITION_CONTINUE_BUTTON}         id=btnContinue

# Risk Questionnaire Page
${OCCUPATION_DROPDOWN}               id=occupation
${REASON_DROPDOWN}                   id=reason
${DYNAMIC_FIELDS}                    id=dynamicFields
${RISK_CONTINUE_BUTTON}              id=btnContinue
${REVIEW_CONTENT}                    id=reviewContent
${BTN_EDIT}                          id=btnEdit
${BTN_CONFIRM}                       id=btnConfirm

# E-Contract Page
${CONTRACT_NAME}                     id=contractName
${CONTRACT_ID_CARD}                  id=contractIdCard
${CONTRACT_NUMBER}                   id=contractNumber
${ACCEPT_CONTRACT_CHECKBOX}          id=acceptContract
${BTN_ACCEPT}                        id=btnAccept
${BTN_CANCEL}                        id=btnCancel

# OTP Confirmation Page
${OTP2_PHONE_DISPLAY}                id=phoneDisplay
${OTP2_REFERENCE_CODE}               id=referenceCode
${OTP2_INPUT_1}                      id=otp1
${OTP2_INPUT_2}                      id=otp2
${OTP2_INPUT_3}                      id=otp3
${OTP2_INPUT_4}                      id=otp4
${OTP2_INPUT_5}                      id=otp5
${OTP2_INPUT_6}                      id=otp6
${OTP2_RESEND_LINK}                  id=btnResend
${OTP2_CONFIRM_BUTTON}               id=btnConfirm
${OTP2_ERROR}                        id=otpError

# Success Page
${SUCCESS_ICON}                      xpath=//div[contains(@class, 'success-icon')]
${REFERENCE_NUMBER}                  id=referenceNumber
${REGISTRATION_DATE}                 id=registrationDate
${BTN_FINISH}                        id=btnFinish

# Multi-URL demo - element locators only (URLs from LDP_UI.yaml)
${GOOGLE_SEARCH_INPUT}              name=q
${FACEBOOK_EMAIL_INPUT}             id=email
${FACEBOOK_PASS_INPUT}              id=pass

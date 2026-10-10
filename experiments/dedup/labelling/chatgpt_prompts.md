# Frontier-LLM labelling (blind, exact human instructions)

1. Open ChatGPT with its strongest model. Start a NEW chat for every prompt.
2. Copy everything between the ``` lines of one prompt and send it.
3. Paste the reply, unedited, into chatgpt_replies.txt under the matching '=== reply N ===' line.
450 reviews in 45 prompts. Write the model name on the first line of chatgpt_replies.txt.

## Prompt 1 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 120 (Zendesk): "Chats time out after 5 minutes and we cannot respond to our customers. 4 months of subscription is already lost. I need someone to reach out to me urgently."
id 306 (Zendesk): "This app needs to basically be rewritten from scratch. The notifications, back button UX, and navigation all make no sense. Further, the performance is really horrid in terms of simple things like loading a ticket. Needs a complete do over and if the developers are being honest, they probably know it."
id 139 (Zendesk): "Hard to use"
id 268 (Zoho Desk): "Another app? Every time I want to do something, as minor as it may be, I have to install another app. This is ridiculous. Let me use a browser istead of redirecting me to install the app. Give me a choice. I've so many gd apps on my phone it's impossible to keep track of them."
id 117 (LiveAgent): "Dos this only work on hosted accounts? We bought the enterprise edition, host it ourselves and cannot access the app at all."
id 249 (Zendesk): "Poor app . Macros not working"
id 352 (Zendesk): "1. Macros don't work,  2. Can't update any field, 3. Always getting errors while submitting tickets"
id 128 (Zendesk): "how to creat an account?"
id 289 (Zoho Desk): "Slow, constantly buggy. ugh I hate this app."
id 315 (Zendesk): "I have downloaded the app but its not allowing me to signin for my domain"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 2 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 198 (Zendesk): "not happy with the mobile app because old chats don't display like it works on the web. now app is for convenient, right ? so if I made a chat yesterday and today if I want to see that and in the app it doesn't load so it's really not very helpful. another thing if someone send a picture and make a text it doesn't show text only the picture."
id 390 (Zendesk): "#BreakingCodeSilence #Team"
id 125 (Zendesk): "I can't sign in. Don't know why writing invalid sub domain or sub domain not found"
id 227 (Zendesk): "This morning the app kicked me out and I'm unable to log back in. When I click to add the address the app does not respond it's frozen."
id 341 (Zendesk): "Notifications are no longer reliable. I have keep checking manually. Not sure what's going on, but the notifications have been terrible for the past 4 months."
id 64 (Freshdesk): "Latest version just crashes on opening. another FAIL from Intuit!"
id 91 (Help Scout): "I agree with other reviewers here. It takes a lot of time to load."
id 435 (Freshdesk): "Domin not support"
id 30 (Freshdesk): "Not working. Asks a browser to login even I have some browsers like firefox opera etc . Thanks."
id 26 (Freshdesk): "Having huge issues where deleted / spam tickets keep coming back. Delete 10 tickets in a row, refresh and they come back! Totally wasting my time deleting the same ticket over and over. Please fix this!"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 3 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 264 (Zoho Desk): "Keeps asking me to create a portal when I am trying to log in to it. No way of signing in to raise tickets"
id 408 (Freshdesk): "Notifications haven't worked since the October update. Customer support acknowledged the issue but two updates later it's still not fixed."
id 148 (Zendesk): "Sleazily forwards people to the google app store if they say they like it and forwards them towards a private feedback form if not. Rating this one star to help unbias the rating."
id 432 (Freshdesk): "The filter functions on this app are atrocious. Makes it completely unusable for me. Why don't you have the same filter functions as the web version does?"
id 112 (LiveAgent): "The app no longer works, just show "initialising" message on screen. It does not log u in"
id 302 (Zendesk): "It does what it is supposed to do, but suffers from dreadful lethargy. It really is very slow. And closing a ticket is not intuitive. Update 2022: even slower. Not worth the bother. Use the Web version rather. Up date mid-2022: uninstalled this junk. Useless"
id 164 (Zendesk): "You cant even submit a response. It keeps failing after 5 tries."
id 65 (Freshdesk): "Made a sales suite demo request on Dec 30th. It's been 3 weeks. All i hear from the support team is that they're trying to get me an acc manager. I've been promised 3 times saying it'll be tomorrow, freshwork is not interested in new client??"
id 254 (Zendesk): "ZERO features for admins, only (extremely barebones) replies for agents with an interface that has considerable differences from the web-based one. With absolutely no support for admins on the go it will be years before this app is usable."
id 258 (Zendesk): "Tickets won't load a lot of the time which makes the app highly unreliable for providing a quick response to customers. Have to rush to a laptop too many times"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 4 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 368 (Zendesk): "It would be a lot better if there was a dark mode. Also, it's hard to find my tickets versus other team members. There's not a clear way of selecting each team members tickets."
id 77 (HappyFox): "It's better than it was but still severely lacking! I still can't search for tickets...? No filtering?"
id 426 (Freshdesk): "There is no option to filter the tickets agent-wise. Could have been useful but I'll have to stick with web version or move to a different platform."
id 163 (Zendesk): "Can't login through my id, earlier used to login through same id. I can use it through web but not through the app"
id 201 (Zendesk): "Opening settings&gt; notifications crashes the app every time, even after uninstalling and reinstalling.  Have to uninstall permanently because I can't turn off notifications outside of business hours."
id 36 (Freshdesk): "Cant view tickets assign to me. List is empty when filter enabled. App is unusable with thousands of tickets."
id 4 (Freshdesk): "I had happily used fresh desk for a year. I recently reached out about changing my subscription. This was there weeks ago and still no one had contacted me about resolving this. This latest update also doesn't work well. It notified me about tickets that are auto deleted It never used to do this. The notifications on the app are is empty but my cell phone died dozens of notifications that I need to clear in the app, but can't. Hopefully someone will respond to my emails now."
id 334 (Zendesk): "I can't use this app. Whenever I logged on it shows acces has been revoked and signed out automatically"
id 283 (Zoho Desk): "NEVER try this app, phone number is required and they DO NOT STOP CALLING YOU it's actually ridiculous, blocked and reported as spam but they keep using different numbers"
id 118 (LiveAgent): "difficult to sort tickets and join a live chat in a timely way."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 5 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 323 (Zendesk): "Macros wouldn't apply on this mobile app. Ridiculous when you can specially make use of it while on the go, resulting in faster response to clients. I no longer have any use for this app as I don't want to type in a reply with tiny mobile keyboard. 🤦‍♂️"
id 272 (Zoho Desk): "App is slow, and keeps closing."
id 221 (Zendesk): "Broken after latest update. Ticket screen just shows up blank after Sept 4th Update. I can only get to tickets by selecting notifications, but if I go to any other view, no tickets are shown. Downgrading Review to One Star. I've had a ticket open on this for 7+ Months and it's still unresolved. Supposedly the engineering team is "looking into it.""
id 440 (Freshdesk): "My company uses this for tickets. This app has been great until this week when they released version 9.0.0. Now I cannot see my tickets on Android devices no matter what I do. It will show me how many tickets there are in my group but I cannot view them."
id 429 (Freshdesk): "Not user friendly , I didn't like it Web is better"
id 21 (Freshdesk): "why can't notifications be deleted? this is a waste of space on my phone"
id 387 (Zendesk): "Can't login using this app, using the website works but the app never sends the code to my email."
id 216 (Zendesk): "Before you could have used the App over data but now only on wifi. You get the notifications but can't respond until you have wifi. Really disappointed ."
id 147 (Zendesk): "I don't like it 😐"
id 354 (Zendesk): "Terrible functionality, can't access live chat support, only tickets. And when I click on tickets I can't even fully see them or reply to them even though I have administrator priveleges"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 6 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 138 (Zendesk): "Keeps on logging out so frustrating. It doesn't keep session token. this particular version sucks"
id 82 (Help Scout): "Doesn't work and was never told. We've been missing emails for weeks now. 

The app doesn't open. I deleted and tried to reinstall but the reinstall 

won't start. Love helpscout but this is ridiculous"
id 373 (Zendesk): "Terrible UI. If you use the desktop version a lot, this mobile app is kind of confusing. There needs to be a way to make it more user friendly"
id 156 (Zendesk): "I am unable to use this app in my phone when I login it's shows error but my ID and password is correct because I am using this zendesk on my laptop can anyone help me???"
id 437 (Freshdesk): "Needs a dark mode."
id 209 (Zendesk): "Why cannot sign in, and cannot type anything to input the url domain.. so bad"
id 320 (Zendesk): "Unable to login since the domain that we use contains a hyphen, and you guys don't allow hyphen in the field. Very basic requirement!"
id 255 (Zendesk): "Recent updates do not allow me login.  The was very useful until the last update but now it has become completely useless. Hope they fix the issue quickly."
id 389 (Zendesk): "will not install"
id 14 (Freshdesk): "Unwieldy to use both, web and app version. Too many notifications for the same ticket. Unable to customize information visible in ticket list. Many more features I don't like. Initially I tried to work with the web team by giving them feedback, but that went nowhere. Not a fan."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 7 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 301 (Zendesk): "Bulk edit update is laughably featureless. Features that bulk update needs to address: assignee, agent group, category, and almost any other field that I can bulk edit from the desktop app. We still need to be able to adjust notifications so we only get alerts on tickets assigned to ourselves and not the entire group. I don't need to know when someone responds to a ticket assigned to someone else."
id 29 (Freshdesk): "Still, no dark mode."
id 53 (Freshdesk): "Not reliable to some extent, keeps on failing...most of the time"
id 324 (Zendesk): "I can't sign in with google and email, this app needs an update"
id 38 (Freshdesk): "URL login not working"
id 211 (Zendesk): ""An agent is taking to this customer." - I'm the only agent and I can no longer reply to tickets when I'm out and about. This CRITICAL bug needs fixing yesterday!!!!"
id 372 (Zendesk): "Can't login"
id 129 (Zendesk): "They flagged my email for nearly everything they touch. Weather it be copper app or purchasing from Bethesda (fallout game merch) your accounts will be messed with, customer service will respond to aid with, do you still need help? but then never respond besides that. I have wasted many hours because they actually are attacking me. I am unsure what transpired to be shadowbanned from so many places but I want others to know to tread carefully, because they are the worst."
id 24 (Freshdesk): "Fraudulent app,looks like they sell your data without consent. Started receiving emails and spam calls from unknown numbers with 2-3 days. Reviews seem to be fake/paid"
id 407 (Freshdesk): "After every update the app misbehaves Have to reinstall it everytime. After the recent update it automatically sign out from the app and ask to authorise again again and stuck in a queue. Also few basic options are missing like to edit the existing note added over case. To notify existing note to someone by simply editing it again."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 8 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 406 (Freshdesk): "App must have feature to manage agents which was alligned for the task. It will help to on and off Freshdesk for agents"
id 292 (Zoho Desk): "You can't unread the ticket from the mobile application"
id 196 (Zendesk): "why Public is default reply now?and where is the preview?"
id 237 (Zendesk): "When an agent includes a link, it just shows as plain text instead of being hyperlinked. Please fix this."
id 71 (Freshdesk): "I reinstalled the app as it was being discontinued on the 18th of October. After reinstalling, I'm unable to log in. Please fix. Thank you."
id 290 (Zoho Desk): "ok at best"
id 410 (Freshdesk): "No dark theme"
id 395 (Zendesk): "Logs out every few hours. Really inconvenient."
id 154 (Zendesk): "doesn't work, fix jt"
id 89 (Help Scout): "When using the Helpscout app on an iPad it has two columns and it's optimised to use for the bigger display, but on android its just a stretched out smartphone app with very limited functionality. Will the Android app get two columns too or is iOS more important to the developers?"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 9 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 296 (Zoho Desk): "Waste app"
id 251 (Zendesk): "Using my android tablet just throws me out when I try to login with "access token has expired or been revoked".  Works fine on my iPhone or logging in on PC"
id 447 (Freshdesk): "Super super app..gave one star"
id 189 (Zendesk): "Cannot create ticket!!!!"
id 423 (Freshdesk): "Missing so much functionality. Major needs that would make agent life easier: Proper time and date on the original ticket. Not knowing when the ticket came in is very frustrating. Dark mode.."
id 347 (Zendesk): "I have ordered a item 2 times cuz my first package was lost and no one offered to replace it nor refunded it back so I just ordered it again and nothing still and I order to talk to support u have to download this app"
id 383 (Zendesk): "It's been a few years since this software was introduced at work. It's the most suffocating, restrictive, trying-to-be-smart, non-intuitive and unhelpful system I've ever had to use."
id 187 (Zendesk): "It shouldn't take a decade to upload or add attachments."
id 273 (Zoho Desk): "This is probably the worst app in the Zoho suite. I love the other apps, this one needs work. Sad I'll have to use an app from another provider. Would have loved to run everything on Zoho."
id 144 (Zendesk): "Extremely lackluster and confusing GUI and UX. The ticket sorting and filtering is appalling."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 10 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 417 (Freshdesk): "Needs better filters. The app works ok but the lack of filters mean I see all jobs for all sites and they'd no good way to filter sites by group. Other than that glaring oversight it's a good app."
id 158 (Zendesk): "I can not login to this moble app. Tryed resetting password, Different emails, Different domain names nothing this for some reason keeps telling me that there is a login error."
id 265 (Zoho Desk): "Cannot view tasks, only tickets."
id 322 (Zendesk): "Not worth the bother can't log in or create account can't read what other people have ticketed on zendesk"
id 130 (Zendesk): "recently the keyboard typing has gone crazy, random capitalisation, moving the cursor, almost like it's resetting the keyboard. I end up not typing in the app 9/10 times now because it annoys me too much. needs fixing if possible"
id 326 (Zendesk): "Unable to login."
id 217 (Zendesk): "Missing tablet mode, if I want to use landscape mode I have to use the website which often does not work well on mobile (drop down menus appear and disappear without allowing to select an option). Pretty inconvenient when you are trying to type and the app forces you to use portrait mode so your text box is covered by the onscreen keyboard. Poor design choice."
id 275 (Zoho Desk): "Does not work the same on the phone as it does on the pc. Everytime i try ans sign in i have to redo the application from scratch not helpful at all"
id 141 (Zendesk): "I tried to use the WhatsApp api but this app has the worst integration, they sell a service and deliver a totally different thing, if you want any additional, you have to pay double for it! I tried to cancel but they keep charging me!! In addition to that, the app manage customers as tickets, a very confuse way to track the customers and the solutions."
id 76 (HappyFox): "Terrible experience, tickets load slower than downloading an imax movie over 56k dial up"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 11 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 152 (Zendesk): "Was Not able to login. Our organization have hyphens in the link of zendesk and its not allowing me to put hyphens. I tried using Google keyboard, default keyboard and swift key keyboard. Then found a workaround. Wrote the link in notes and then cut pasted here and then it allowed me. You guys need to improve a lot."
id 23 (Freshdesk): "Uninstalled and stopped using it. The app forces me to be tracked by google (via recaptha) otherwise it refuses access."
id 450 (Freshdesk): "Freshdesk has not been operational for almost a week! they cannot commit to a timeline of when it will work again. cannot login or do anything in the system so paying for nothing right now"
id 259 (Zendesk): "Phone replies regularly disappear / do not show in the past 2 months. I simply write and post them and they do not show later."
id 105 (Help Scout): "I remember when that was still good. Now it takes 30+ seconds to open a message"
id 263 (Zoho Desk): "Cant close a ticket when i close the ticket it opens right back up anf vice versa"
id 418 (Freshdesk): "Terrible login design - instead of having a functioning login page, finding the right one using their 50 million different domains associated with accounts is like a 4-step maze every time. Then they go and discontinue their free plan for a product that's far less functional than alternatives. Thanks for motivating me to build our own support ticketing system in-house. Your terrible design and greed did some good, at least."
id 331 (Zendesk): "App is extremely slow to open tickets. UI needs a lot of work, it's 2024 it's not that hard to Build a good efficient user interface but as we know Zendesk is slow af to implement changes and feedback. I use the app begrudgingly. Fix up!"
id 37 (Freshdesk): "Says access denied most of the time I want to use it. I have to uninstall and reinstall every day!"
id 256 (Zendesk): "There was only one good thing about their app, that was notifications on mobile app.. This too they removed after latest updates."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 12 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 175 (Zendesk): "Can't login due to ip restrictions, unsure why since can login to web site. Unfortunately the web site on mobile browser is also pretty unless as well. Certainly not fit purpose"
id 199 (Zendesk): "I can't logged in on this app. When i try to log in message appears "Access has been revoked""
id 111 (LiveAgent): "Doesn't work"
id 172 (Zendesk): "What idiot changed the icon to some generic nonsense and changed the name of the app to Support?"
id 47 (Freshdesk): "I'm not receiving the calls itself."
id 270 (Zoho Desk): "I emailed support with no response and it's been a week."
id 134 (Zendesk): "Awful updated view, the ticket's views are all over and not user friendly. Now Public Reply and Internal Notes are mixed and the views are so sensitive. What's the point of having the Zendesk chat's status on the main page but the actual chat being on a separate page?! This makes no sense in splitting information between 2 separate tabs/pages."
id 97 (Help Scout): "I have the same issue as Dean E. Version 2.1.0 Most of the time you tap on an Android notification it takes you to a blank white screen or says there is a mailbox error. Without working notifications I might as well just browse to the website."
id 110 (LiveAgent): "No notification when someone sends a ticket or start the chat. There is no point in having an app if it cannot give basic notification when a ticket arrives. Zendesk is 10x better"
id 87 (Help Scout): "The last version doesn't work on my phone"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 13 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 18 (Freshdesk): "Can't get anywhere ir help from anyone"
id 6 (Freshdesk): "It still needs a lot of improvements."
id 348 (Zendesk): "Despite providing proper email and password still it's not accepting and shows error invalid credentials.  It's happening after latest release pls fix it or I'll have to uninstall"
id 239 (Zendesk): "Doesn't let me in."
id 380 (Zendesk): "Useful app until recent update...now routinely logs agents out, or doesn't work at all don't bother using until fixed...."
id 267 (Zoho Desk): "Update 2/1/22 Like all Zoho products support is not easy to even locate let alone contact. If you do reach someone they have no idea how to use the software and are only able to paste pre written responses."
id 425 (Freshdesk): "Asking me for URI link otherwise will not go next step... i just wanted to try it out .. so, big uninstall for you..bye bye"
id 338 (Zendesk): "Even after update to latest version can't change on-call setting EDIT: 3 years later, I have no idea how, ZenDesk managed yet again to keep it on the top of the worst apps I've ever had on my phone. This app usea 98% of the CPU and RAM on my Essential phone."
id 291 (Zoho Desk): "Unable to acces in phone"
id 414 (Freshdesk): "Bakwaas"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 14 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 416 (Freshdesk): "This app maybe reviewed to make it user friendly.."
id 238 (Zendesk): "The app keeps logging out multiple times a day for no apparent reason. Very annoying. We need a fix ASAP please."
id 40 (Freshdesk): "Not getting any notification"
id 27 (Freshdesk): "they hacked my email and sent emails to every single contact in my gmail"
id 13 (Freshdesk): "The app keeps crashing after a recent update... 03/21/22 - Still keeps crashing while clicking on menu to Edit a ticket."
id 288 (Zoho Desk): "Cannot even tag people correctly within the app (like you can on desktop - literally doesnt even register it even when you do it the same as on pc), doesn't work with an email signature without it automatically formatting it a weird way (like as an email thread). Would be a good app, but it's so buggy you'll have to use the desktop version anyway"
id 166 (Zendesk): "Hello, I'm using this app, and for about few days ago, it doesn't work! I don't have notification, sometimes i have...but sync is late. Can you fix this?"
id 374 (Zendesk): "Since the last update in March, I am having issues. I can no longer turn on the notifications for my groups or for all in the settings. It jus takes me on and endless loop and the button will not turn on no matter what I do. please fix this!!"
id 45 (Freshdesk): "This new update is horrible. I can't easily discern new tickets anymore. Also the wasted space in this layout means I can only see 3-4 tickets on the device screen at a time now. Please revert this"
id 78 (HappyFox): "Lacking Core Functionality present in the first version of the app. Obviously an attempt to streamline and modernize the app, but clearly not yet ready for primetime. Cannot make a new ticket, in a solution 100% focused on helpdesks that use tickets. That alone is enough to not use this version of the mobile app. The old version allows making tickets, but does not work on android with SSO. The old iOS version does both."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 15 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 69 (Freshdesk): "Navigation is terrible. I don't even bother using the app. I just use the browser"
id 377 (Zendesk): "Cant make or receive calls on mobile app. Thats is most important. Get the dialer in the app."
id 278 (Zoho Desk): "Keeps on crashing whether you select biometric or pin based login unreliable app, will let you login once in a while. tried atleast 100 times, was able to login a few time, rest crashes."
id 52 (Freshdesk): "NEW BUG: The refresh function at the ticket queue page is gone! Used to be able to slide down to refresh but can't do that anymore. EXISTING PROBLEM: It'd be great if we can see all the detailed information like company details, notes, etc exactly like the website. Even though you can access the contact details and all, there are still a lot of information missing in the app, its not as thorough as the website. Also, it would be really helpful if the app have the dashboard like the website."
id 243 (Zendesk): "Can't use SSO."
id 74 (Freshdesk): "the apps require a lot of time to edit and sending the email. USELESS!!!"
id 274 (Zoho Desk): "Zoho desk is not working in android I used to have iPhone it works perfectly in ios and it doesn't work in android please fix the issue"
id 309 (Zendesk): "Just keeps crashing after the recent update."
id 419 (Freshdesk): "Couldn't login. 'Please try again' is all I get"
id 365 (Zendesk): "This still have many error cannot login from Google and always said email and password login error, but when try to login from browser si working. This apps suck"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 16 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 391 (Zendesk): "Not Great- 2 main issues. 1. The cc field in the ticket app has disappeared. 2. You can start a reply and then leave the app to get more information or to copy something to come back into the app to paste in the ticket response you started. As soon as you leave the screen all text is deleted."
id 353 (Zendesk): "this app closes imidiately i sign in"
id 219 (Zendesk): "Useless"
id 340 (Zendesk): "Waste update"
id 50 (Freshdesk): "Crashing every time"
id 226 (Zendesk): "Should be able to answer customer chats and texts from the app. No longer able to see recently solved tickets. the pull doen is not working on my Android, can only see unsolved tickets."
id 236 (Zendesk): "How can app have no horizontal mode and screen rotation? Useless with any tablet and keyboard."
id 329 (Zendesk): "This PoS app keeps telling me I have no Internet connection, when I do... So I can't open tickets a majority of the time. I can use many other cloud apps fine, so it's definitely not my Internet connection. This has been going in for weeks."
id 202 (Zendesk): "The old app was much better!! User experience is real bad. When looking at tickets from all groups, it lumps them together instead of showing by group and there is no way to organize it properly.  Conversations are shown oldest to newest, top to bottom which is frustrating. You have to uncollapse Conversations and scroll all the way back to the bottom to view the last comment.  Opening up tickets outside the app doesn't actually bring you to the ticket, just opens the app to your home screen.  Just poorly designed. Bring the old one back"
id 136 (Zendesk): "Not useful for us as admins.. I couldn't assign work for my agents from it, which was very disappointed"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 17 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 369 (Zendesk): "App is useless."
id 300 (Zoho Desk): "worst app... especially in pc. takes 20 times for single reply... so irritating..."
id 101 (Help Scout): "Can't update. Locked out."
id 332 (Zendesk): "Doesn't turn sideways on tablet."
id 384 (Zendesk): "What happened to this app? It used to work fine, but now it just launches my mobile browser once I'm logged in. It used to show an actual app interface, not launch the website."
id 108 (LiveAgent): "The app keeps telling me oops the URL is invalid when I know I'm putting in the right URL. So at the moment the app is useless to me."
id 223 (Zendesk): "Experience is very different than the web version. Some options are missing. And I cant even use it on landscape mode."
id 56 (Freshdesk): "Unable to sign in. UI shows sso option & when you click on allow it doesn't get logged in and an error comes."
id 124 (Zendesk): "the app doesn't work. it will not let you click on any tickets. it says there is no internet connection."
id 35 (Freshdesk): "Basic functions work, but: CSAT ratings not visible in mobile app :( Also splitting tickets does not work. Why? Searching for a valid ticket number brings no results! Customers tell us please check ticket 12345 and we cannot do that. Also find no option to configure that external links are not opened directly in the Fresh desk app."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 18 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 317 (Zendesk): "I can't respond to the incoming tickets. It shows "no internet connection" when there is!"
id 284 (Zoho Desk): "Hi this app paid service or free"
id 205 (Zendesk): "I hate this app"
id 113 (LiveAgent): "Very limited making it worthless"
id 212 (Zendesk): "The new app is bad. Bring back the old app!"
id 401 (Freshdesk): "Pretty poor and clunky - but what really annoys me is paying for an application that constantly pops up a message saying 'Please Rate The App' - it gets in the way of doing what I paid for. Spamming paying customers with notifications is not cool, at least put an option in to say 'stop doing this'..."
id 102 (Help Scout): "Keeps saying I need to update. I can't get out of the loop."
id 449 (Freshdesk): "doesn't really work anymore, can't mark anything as spam and can't see special custom fields, can't merge either"
id 142 (Zendesk): "Images in tickets don't render"
id 311 (Zendesk): "Aweful"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 19 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 421 (Freshdesk): "I am not able to install Freshdesk app."
id 314 (Zendesk): "Cannot apply macro after recent update."
id 39 (Freshdesk): "Currently unable to have notifications from the app with the latest release. There was a bug that forced me to redownload and install, and now I can't toggle notifications from the settings menu in my S23 Phone. Please fix this, as those notifcations are crucial to my job."
id 436 (Freshdesk): "It doesnt allow me to log in"
id 321 (Zendesk): "Notification sound stops playing after some time, which means I am not able to keep track of new messages. Happened on all my devices, which makes me think it's a bug. Notifications appear in the 'event log', but there is no sound for incoming messages. To fix the problem, I need to clear cache and data for the app, for the sound to come back. But this fixes the issue only temporarily."
id 191 (Zendesk): "Can't understand why the status of the ticket (pending, open etc) is now removed from the views. Makes the views pointless as a viewing platform as you then need to inspect each ticket individually to see if it's been changed. Renamed app is a balls up too. It searching the app store for the name 'support' you will get bored before finding it. Conversely search for the name 'zendesk support' on your phone and you won't find the app on your phone. Don't bother installing. It's easier now to go to the website"
id 169 (Zendesk): "When I try to sign repeted error invalid email and password time waste  Still not solve my issue"
id 48 (Freshdesk): "The analytics filters are a pain to use, if they work at all. Most times I end up having to resort to the web version, which defeats the purpose of having a mobile app. The app shows as "Support Desk" in my library. Name it Freshdesk, please. We all have too much going on to remember your cutesy nickname when we're trying to get work done."
id 285 (Zoho Desk): "Worst app, not working properly and ticket raised is not responded till now"
id 224 (Zendesk): "Keeps telling me that my token is expired or revoked and signing me out. Please fix."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 20 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 303 (Zendesk): "Loses all text when switching apps, making it difficult to lookup important details. Text input window is small and no option for expanding"
id 307 (Zendesk): "Doesn't work well on mobile app with ujet connection."
id 1 (Freshdesk): "Can not select what team to assign the work order to any more, the box shows up, but you can not scroll down to select any teams."
id 409 (Freshdesk): "Really buggy and cubersom. Copy /Pasting is broken and changing ticket status is a pain."
id 204 (Zendesk): "not taking my email"
id 33 (Freshdesk): "Difficult to login to this app ...."
id 70 (Freshdesk): "bait and switch"
id 228 (Zendesk): "Has potential, but seems like it's only 60% done. I'm no longer able to see photos and attachments in the app, but they appear fine in web browser. This is critical because customers and Tier 1 support collect screenshots and we're unable to review them without a PC."
id 93 (Help Scout): "App just crashes whenever I open it. Not only my problem too, it the same problem with my colleagues who have different android phones"
id 137 (Zendesk): "Trying this 2 years later again, and it's still as buggy, slow, and unresponsive as before. Will probably go back to Gmail soon."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 21 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 397 (Zendesk): "Cant even log in"
id 85 (Help Scout): "It forgets my login credentials again and again. I logged in this morning and 10 hours later it again tells me I have to log in again. This is super annoying and makes the app pretty useless."
id 304 (Zendesk): "My sister brother don't waist money for that apps to use he is big liar and cheater he give people money to get like only but apps Sam Ur number one cheater ur apps is same like as you toys  you play with people get money but not solve problems  my imei  still problems I give money already at you but still block my network god see you god give you much punishment for you then you know  that ur do it's good or not  number cheater apps don't download any people you waist money for that apps my"
id 161 (Zendesk): "worked fine prior to desktop update. unable to change phone status in app. toggles you offline when you sign out/close desktop tab"
id 83 (Help Scout): "Stopped working after the update."
id 207 (Zendesk): "Barely works, barely functional, disconnects frequently."
id 107 (LiveAgent): "No longer works. This app no longer works. I can't open it as it just hangs. Tried rebooting my phone and reinstall but that didn't help. Too bad because I used it all the time"
id 225 (Zendesk): "Not very easy to use. Unlike web site."
id 194 (Zendesk): "Not the app I was looking for"
id 358 (Zendesk): "Harold is complete failure and will not grace me with a reply to my questions, I've had better customer service at McDonald's"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 22 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 297 (Zoho Desk): "Useful if only managing email based tickets. Or as a glorified notification app. Can't make outgoing calls using the CS number or sms tickets"
id 293 (Zoho Desk): "Can't copy text or links from tickets.....nice"
id 327 (Zendesk): "de la noche a la mañana, ya no deja iniciar sesión con error "not found"...."
id 153 (Zendesk): "There is no way to change auto refresh to manual. After viewing a ticket and returning to the View page, it always refreshes first. Frustrating to go through multiple tickets when you have to wait everytime before you can see the next tickets."
id 16 (Freshdesk): "Please install a browser to sign in, not sure if this is a bug with sso but the app can't sign in, works fine on browsers. I use this for work and this is very annoying."
id 313 (Zendesk): "Previous employer used Corrigo current employer uses this app and it's awful. Creating your own work order is a disaster as you have to go into multiple screens to fill out the info. You should include sort by location as an option to sort work orders. Currently if a work order is put in by a dm it comes up separately. Work orders that are on hold and paused should be in a separate category and you should add a deferred maintenance category. Having them all clumped together is messy."
id 123 (Zendesk): "I can't enter our zendesk subdomain as it contains a hyphen"
id 178 (Zendesk): "What happened to the notifications??"
id 79 (HappyFox): "Have to login everytime I open the app. Using SSO login."
id 247 (Zendesk): "As of today (11/23) I am forced to use a google login for this app, even though our private instance of Zendesk does not require that for agents. Because of this, the app is now completely worthless."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 23 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 355 (Zendesk): "I cant login the app.. Its appear acces been revoke.. But in website i can login.. Kindly please check why this happens. And why i cant purchase.. Everytime i click to buy its appear page not found"
id 388 (Zendesk): "No option to set ring tone to get louder notification There's a delay in getting tickets"
id 346 (Zendesk): "App has 78 Trackers!!!???!! Why would u put 78 Trackers for this! What kind of information are u guys collecting and selling us our to? It does the job but 78 Trackers are real bad"
id 422 (Freshdesk): "Canned responses are broken. I make heavy use of them in my work and variables contained in a canned response print the literal variable name instead of the relevant associated metadata for that ticket, like the requester of a ticket's name. This effectively makes the app useless for anything productive on mobile. You're better off using their buggy web interface."
id 333 (Zendesk): "poor tablet experience - needs to be updated"
id 34 (Freshdesk): "buggy for months. ticket view always out of date. unreliable for keeping on top of ticket statuses and replies."
id 197 (Zendesk): "Really buggy when it comes to pasting or dictating text on Android."
id 109 (LiveAgent): "App don't allow to do anything masive  also the tickets are randomly appear I use the Web version instead. App really need to improvement"
id 262 (Zendesk): "Trying to log in and I am sure that the password and mail is correct but it doesnt work. Very upset."
id 367 (Zendesk): "Needs some serious ui rework, It is just a bit to mobile like, Being a ticket system application it need easy way to navigate across groups of tickets and easy way to sort the current tickets and a way to see all the responses not just the last one.."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 24 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 350 (Zendesk): "Ужасное приложение. Для меня загадка, как имея такие ресурсы, можно раз за разом релизить такое УГ"
id 441 (Freshdesk): "No to much space to add pictures need more space please"
id 25 (Freshdesk): "Annoying notifications. I keep getting a notification for same event multiple times a day, even though there were no updates since I checked the ticket. "Someone responded to your ticket!" Tap notification and it takes me to a ticket that I responded to 2 hours ago that had no updates since. Afterhours? "Someone responded to your ticket. Now. +4 notifications" tap notification, open ticket, this actually happened 3 hours ago. Phone keeps going off all day for no reason. Infuriating."
id 230 (Zendesk): "Macros dont load"
id 32 (Freshdesk): "Be good to have easy access to tickets you created. Not just the ones assigned to you..(access to the customer portal)"
id 213 (Zendesk): "Terrible app experience, more or less unusable. Nearly impossible to navigate to the lost of tickets due to a bug that has been present for about 3 years. the back button doesn't take you to the list of tickets. have to kill the app and restart. Also awkward for general ticket submission. UPDATE: to confirm this has been shared with zendesk support twice and they said that they have no plans to fix. they clearly don't use their own app."
id 55 (Freshdesk): "Unstable app. Always logs out immediately after logging in. Not able to use the app at all."
id 371 (Zendesk): "Nothing is worse than Zendesk. I downloaded the app just to share a review. Whenever I see a company uses Zendesk support I actively seek another provider. You NEVER have your issue solved. You play a back and forth game until you give up in frustration. I equate Zendesk "support" to slamming my head against a brick wall."
id 235 (Zendesk): "Got the latest update a few days ago and ever since, I am unable to login because the built in browser doesn't show the login system from my corporate ADFS system.  I am unable to login without this as it is restricted.  Please fix ASAP."
id 220 (Zendesk): "This morning I was logged out without notice and the app will no longer work. Says "access revoked" when I try to login. Able to login to the website just fine. Seems like the app is broken or they've removed the feature for my license. Again without notice. It's a terrible app anyway thats super limited (no merging tickets), buggy (loses your drafts, formatting issues). I just hate it. Long time user"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 25 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 180 (Zendesk): "How the hell can i sign in if I don't have an account, sign in is the only option,really???"
id 15 (Freshdesk): "Originally five stars. But now showing a popup asking me to give another five stars. I hate these. It's an own goal."
id 342 (Zendesk): "App interrupts you with inane suggestions or request to review while in the middle of using it for work. UPDATE: They still do it. Luckily we are transitioning away from their platform."
id 427 (Freshdesk): "add dark mode I'm unbothered about how... just do it... isn't it a standard in every app 2026? you enjoy the flashbang?"
id 248 (Zendesk): "i couldn't able to login .. the login page is not loading.. i can see only white screen after selecting SSO"
id 103 (Help Scout): "I can no longer use the app. It tells me there is an updated version and to 

visit the play store (no link). I visit the play store and have the up to 

date version. Any plans on making the accessible?"
id 20 (Freshdesk): "In mobile ,In analytics tab, we customised the report , if suppose the report contains any ticket number , then it open the respective ticket and we reply or change anything means it's not working"
id 413 (Freshdesk): "Unable to download... Wanted to access the bbmp covid thing"
id 244 (Zendesk): "Really really slow, weak server"
id 312 (Zendesk): "the refresh or reload never works, always freezes and stops animating. no matter what connection I am on. utterly useless"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 26 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 392 (Zendesk): "if you use the back key of your phone or in a open ticket it closes the app. fix this asap."
id 106 (LiveAgent): "This app is literally unusable. No canned messages, it rings 30 mins after the chat comes through and it does this regardless if the app is running or even logged into. I have force stopped and it still does it. And it has notifications you can't clear even after the issue is resolved. This is an absolute joke from a company that has one purpose. You need to hire some real devs because the ones you have now are clearly not capable."
id 19 (Freshdesk): "Since updating I can no longer login. Contacted support (ticket ref [#7744891]) who initially looked into the issue but have now gone quiet. Wish I didn't update as can't login to the new app, nor roll back!"
id 188 (Zendesk): "App crashes at login. Uninstalled and reinstalled but same issue persists. Nexus 6P"
id 192 (Zendesk): "Just the worst.  It used to be somewhat functional but when it changed to the 'support' app it lost all functionality.  If you can not sort by views there is no purpose to the phone app.  You see all tickets all the time, open or closed.  It's hard to imagine a worse way to organize a helpdesk."
id 434 (Freshdesk): "The calls are not getting connected"
id 360 (Zendesk): "Cannot access the app and get an error when trying to login - the access token has expired or been revoked"
id 150 (Zendesk): "Very bad"
id 184 (Zendesk): "Worst Application I am not able to see all unsolved ticket from last one month using my user ID and pass and there is no customer support number for solving my issues"
id 165 (Zendesk): "These people help scam people out of there money! Along Bluesky and pinebowl they scam people. Be weary lol and now they say that I should reply directly to themselves. This is ! Won't say it. Well do your job and get rid of them"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 27 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 41 (Freshdesk): "Developers do not respond to service issues reported to them in a timely manner."
id 208 (Zendesk): "Keep crashing."
id 364 (Zendesk): "Allow us to modify content of tickets."
id 67 (Freshdesk): "Not great. One of the most important things this app should have is the ability to customise the notification sound for the phone, and this app doesn't have it."
id 179 (Zendesk): "After the last update the organization field does display the organization like it does in the web GUI. Also, after the update if I update certain fields it doesn't update to the web GUI all the time or undo the updates in the GUI"
id 260 (Zendesk): "Notification no longer works on Android after recent update."
id 351 (Zendesk): "Sadly, like many other reviews here, the app states you have invalid credentials when you try to sign in."
id 382 (Zendesk): "I receive "Access Revoked" whenever I log in via app. Better to log in via browser"
id 242 (Zendesk): "Very very bad application, lately very hard to deal with..."
id 415 (Freshdesk): "No dark mode. I have highly sensitive eyes please fix."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 28 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 305 (Zendesk): "App is very limited. We work remote like everyone else now adays and have fir way before the pandemic. Would love ability to monitor techs and calls from app and to not be in front of a PC. Updating tickets, etc. Could be easier but not having the ability to monitor my techs from the mobile app is big issue. I think it could be its own app honestly just for zendesk talk management and have the tools that are available online so I can keep an eye on our support queue without being at a PC 24/7"
id 104 (Help Scout): "App forces me to update but there is no update in Google Play. Totally useless"
id 155 (Zendesk): "After latest update the tool got stuck/hangup in loading....not able to navigate any views. Has the issue been fixed? Because still am facing the same instance :( customer support is a joke for Zendesk firm..."
id 12 (Freshdesk): "8.8.2 has bug with Android app. No notification even though everything allowed. Switched back to 8.8.1 and now working fine."
id 252 (Zendesk): "Slow and stuck on portrait"
id 261 (Zendesk): "Ever since a recent update the app is unusable. In order to login it creates a browser interface to go through the SSO/OneLogin/MFA process, but never actually logs you in on the app. You are left with a browser OneLogin screen with a link for Zendesk, which it tries launching in a browser popup.... It never redirects to the app. When you X out of the browser, the app is still waiting for you to sign in. It's useless."
id 143 (Zendesk): "Cannot login. Says domain doesn't exist. No clear way to contact support"
id 433 (Freshdesk): "cannot login, alwasy say "something wrong""
id 403 (Freshdesk): "App is waste notification is not working"
id 72 (Freshdesk): "Worst app, no filters are there to sort your tickets with your name and other UDF's and to reply accordingly. The FD web version is good but the app version is totally pathetic. I am unable to understand if the FD team is even watching what the hell they have created with this app😡"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 29 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 257 (Zendesk): "The fact that the app just shows up as "Support" in my app drawer now is stupid. Make it Zendesk again, stop trying to do clever branding BS on mobile"
id 240 (Zendesk): "Not logging me in"
id 376 (Zendesk): "Mobile app sucks so bad. You cant view anything but your own (agent) tickets you can't view the group open tickets and you can't use the macros at all. Total garbage. Better to use a browser in desktop view which still sucks. Going to have to stick to still just using my laptop to manage tickets."
id 282 (Zoho Desk): "Not nearly as useful as it could be. The UI/ UX needs a lot more work"
id 366 (Zendesk): "It's better than trying to use Zendesk in a browser on you phone. Nothing else positive to say here however. ways and means for finding a ticket by other than reading down a list should be the first enhancement."
id 393 (Zendesk): "Mobile compatibility is extremely less, much more expected from Zendesk and its developing and testing team"
id 174 (Zendesk): "I only have 1 email address. Your saying it's wrong, hello what other email address do you want?"
id 428 (Freshdesk): "The added notes and summary is not viewable in app Canned responses are not available for mob version"
id 299 (Zoho Desk): "Ridiculously slow and annoying. I can't work as fast as I used to. Please fix it."
id 402 (Freshdesk): "Ticket 12816421 raised, more than a week, no closure yet."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 30 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 157 (Zendesk): "Absolutely trash app. Can't use Macros. Updates sent on a ticket don't show up for upto 10mins. Sorting doesn't work properly."
id 51 (Freshdesk): "Why does the new version not exit on back button? I hate it....."
id 145 (Zendesk): "I am unable to login to check.my ticket."
id 114 (LiveAgent): "Its not working again. Doesnt even starts."
id 42 (Freshdesk): "Cannot filter open tickets"
id 86 (Help Scout): "Had to update now stuck in a horrendous loop of nothingness. Unusable since update worked ok before which was better than now and no its not fixed on my end nor any others end..."
id 88 (Help Scout): "App was perfectly fine, but the latest update means the app now fails to start. I've sent off the error reports, hoping it gets fixed very soon."
id 84 (Help Scout): "Please solve search in app. It almost always displays Server error. No matter of internet speed."
id 250 (Zendesk): "Hardly better than the clunky web application. Slow to use with a limited feature set, and unintuitive user interface."
id 319 (Zendesk): "Not great, but usable. Notifications only come through when the phone is unlocked. It could be a ticket from 15 minutes ago, but only comes through once I unlock the phone. Have been told it's because zendesk devs have not optimized for Google's FCM. Need notifications to come through as soon as a ticket is in, not an hour later when I unlock my phone."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 31 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 438 (Freshdesk): "Would be five star if you haven't taken away one very important feature! "Custom notification ringtone" it was really easy to know when you received a new ticket when you get a sign of special ringtone."
id 195 (Zendesk): "Initial install would not let me sign In or allow any input. Just first sign in button and back arrow."
id 58 (Freshdesk): "Please add dark mode its really annoying not to have such feature at this stage now"
id 115 (LiveAgent): "Images do not show. No notifications. Bad UI and UX"
id 94 (Help Scout): "Missing functions we rely on...Linking to docs being the main one. UPDATE: now fails to load anything...Just a big white screen! Uninstalled"
id 370 (Zendesk): "When are you going to make major improvements instead of "minor" ones in each release? It's been years and it's still impossible to see who's viewing a ticket on the app. Useless"
id 131 (Zendesk): "Absolutely rubbish don't bother with it."
id 126 (Zendesk): "I would give Zendesk app a better review, but you cannot use the App in Landscape mode. The portrait mode is fine for Phone."
id 66 (Freshdesk): "It was all working well until suddenly now the whole notifications pane shows no notifications at all. As an admin, unable to really see tickets due to this issue/bug since the last update."
id 277 (Zoho Desk): "Terrible not even close to cheap ones. Extremely hard and annoying to zoom the text and interact."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 32 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 8 (Freshdesk): "Notification don't show up when a new ticket coming, please fix this"
id 7 (Freshdesk): "It kicks you out then you can't reset password without a act of god"
id 337 (Zendesk): "Possibly the most useless app I've used. Remembers login for about 10 minutes (then forces relogin), doesn't remember the subdomain either, search doesn't seem to work, deeplinks don't work, views don't seem to be updated, and the app doesn't even show up in the regular apps list."
id 159 (Zendesk): "I can't log in to my Zendesk. It keeps saying no found. Error"
id 399 (Zendesk): "I am talking about LIBON  app iam having problems  last few days and they not doing any thing I don't know how can I get my money back"
id 119 (LiveAgent): "Multiple problems just to login. Starting the app doesn't always make agent available. Features are very limited. UI is badly designed, I had to contact support to work out how to use it. For context, I'm a software developer. Support was good but still a poor experience."
id 168 (Zendesk): "Don't even know what this app was 4"
id 344 (Zendesk): "poor design. app opens in an embedded browser and won't stay logged in."
id 95 (Help Scout): "Epic fail on the upgrade guys."
id 279 (Zoho Desk): "The app is so slow. It takes up to 5-10 minutes to update your inbox if it even works. Half of the time it will load of minutes and then show a box "an error occurred, please try again later". The point with an app like this is to be able to check you tickets on the go. So when you are busy and have 10 minutes to check, but you then spent your available time waiting for the app to load instead of being productive, the app just becomes useless."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 33 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 49 (Freshdesk): "I have 2 of 5 the change to log in into the platform. When I login it don't does. Just takes out and today is 2 of 5 times don't arrive to login directly. Bad bad support, as why they mention to me is we don't reproduce it. Even if I show the problem in a video conference with the support team."
id 5 (Freshdesk): "honestly garbage of an app, been flagging the same issue for 5 years now and they didnt manage to apply a fix. what is the point of using the app if you can't close the tickets? each time I select an option on the ticket type field and I try to save, the field resets."
id 121 (Zendesk): "Literally broken...."
id 135 (Zendesk): "DISGUSTING"
id 149 (Zendesk): "I get visual bug where app goes white and can't see letters from menu options"
id 182 (Zendesk): "Why my first response time stuck at 70-75% everyday for 4 months. Even I closely monitor frt for every 2 hours , and reply customer within 30 secs for all tickets come in."
id 328 (Zendesk): "Worst app. Not working properly"
id 381 (Zendesk): "I only ever used the app to check on the status of tickets and then would jump on the computer if I needed to respond, but the latest update removes the colors in the list of tickets that note the current status. The new version is practically useless to me."
id 336 (Zendesk): "I have installed the app but cannot type the subdomain. Not usable at all."
id 361 (Zendesk): "After the last update that you made i didn't got the notification and if i get it its coming with your default sound not from the sound that i required"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 34 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 446 (Freshdesk): "I am not getting a call after clicking on'click here to call the patient'"
id 231 (Zendesk): "I was not able to login on my new phone Galaxy s8. Poor login screen and 

SSO integration :("
id 31 (Freshdesk): "This app never works, I always get an error message"
id 151 (Zendesk): "The new update hasn't been a good experience. Logging in is intermittent, and when I managed to login, the "spinning circle" is all I seem to see. Uninstalled and reinstalled but still no go. And when I do manage to log in, after a little while, the app says I'm logged out? Says my token has expired? What gives! Right now I'm responding back to clients directly via email, the app at the point in time is unusable."
id 133 (Zendesk): "Why the hell do I need to use my google account to sign in!? The email account I use to sign in to Zendesk, which I've used for the last 6 years, is NOT the same as my google account, nor do I want it to be. I can log in to the helpdesk just fine on the web, but I can't log in on the app without specifically using a google account? Whose idea was that? Complete garbage. Now I can't use the app AT ALL."
id 44 (Freshdesk): "They push to buy a paid plan even for legacy users."
id 190 (Zendesk): "Can't use macro's in this app. Without macro's this app is useless. Have to 

type manually in the reply."
id 343 (Zendesk): "Cannot open any ticket. Always shows "unsupported ticket". Useless app."
id 176 (Zendesk): "Now unable to use dual apps after upgraded to Android Pie"
id 316 (Zendesk): "Not able to merge 2 more tickets on Android app."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 35 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 386 (Zendesk): "Can't add CC's by email address if that address doesn't exist in the system already?!?!"
id 442 (Freshdesk): "Our experience with post-sale service and onboarding was disappointing. Onboarding was basic, with representatives lacking a thorough understanding of the product, leading to inadequate training. Support is not readily available by phone, making issue resolution long and time-consuming. Hidden policies in the fine print make changing plans nearly impossible, and these were not disclosed during the sales process. Overall, it has been a frustrating experience, especially from a listed company."
id 345 (Zendesk): "I need to get fully started register for this account, please support, how to make it sign up for free conversation"
id 127 (Zendesk): "Absolutely rubbish. No side view. You would have thought they would support Android tablets since it's highly convenient for business travelers on the go."
id 96 (Help Scout): "Unable to login thru Google SSO and has been an ongoing issue for the past year and a half. If I try a different account that isn't tied to an account it says so but when I use the account associated with it then it just stays on a login loop indefinitely"
id 233 (Zendesk): "App seems to show only pending, closed or all tickets. There is no option to filter new tickets only. How to add that to my views? Support is unreachable via the app. Update: I don't have that option through the Android app. If I tap on the view options from the middle of the screen, it allows me to pick from several types of tickets, but none of them are either 'New' or 'Open' that's the only editing option I have."
id 444 (Freshdesk): "The app locks me from being able to log in quite often"
id 81 (Help Scout): "Forces you to update but no update made and not working 😫😫"
id 349 (Zendesk): "Zendesk exemplifies the "who cares" attitude. Worked with multiple companies using Zendesk and it's always the same... I leave outraged at the company that hired Zendesk. Great customer service Zendesk, no one can drive them away like you!!!!"
id 286 (Zoho Desk): "Can not login to my account which I regularly use daily on computer. Thanks for nothing"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 36 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 63 (Freshdesk): "Still not dark mode!? :( Uninstalled"
id 394 (Zendesk): "Quickie views not visible in mobile app 😓"
id 420 (Freshdesk): "Keeps logging out, not able to use this even for a day. Everytime I open this app it logs me out."
id 271 (Zoho Desk): "It is not getting downloaded"
id 378 (Zendesk): "Unfortunately, the refresh issue is still there. That makes the app kind of useless. Lenovo Tab M10. Schade"
id 177 (Zendesk): "how can I sign in?"
id 445 (Freshdesk): "this app is terrible but shouldn't be too surprised at this given fresh desk is literally the worst help desk system I've ever used. This app just seems to give up on itself and produces a screen that says "it's not you, it's us". When you contact support they tell you to uninstall and reinstall the app. I've now given up on doing this as if they can't be bothered to write a working app then i won't bother using it. display of tickets with more than a few responses is unreadable."
id 404 (Freshdesk): "waiting time is too long than web-based when opening the application"
id 357 (Zendesk): "The new UI in the web interface is terrible. I can't even switch back to the old one."
id 92 (Help Scout): "Re-design appears to have broken pull-to-refresh for tickets, which I'm sure used to exist? This is in addition to temporarily breaking search. Features (like Snooze) continue to be exposed which aren't available for the account's plan, and using these just displays a generic error message."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 37 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 54 (Freshdesk): "App is slow and gives double tickets."
id 160 (Zendesk): "Edit: the app has become blindingly white. I'm downgrading to 1.7.1. 2. The UI is horrible - for every reply I first have to choose a resolution at the top of the ticket and then submit my answer at the bottom. 3. A new update made it worse: the reply form has enough height to show just three lines of text. Most of the vertical space is wasted. Again, the resolution and the reply form are spaced out and it takes an extra scrolling effort for every ticket to adjust a resolution and send a reply."
id 17 (Freshdesk): "This app continually goes downhill. The QC is poor and the support staff are very slow to implement fixes. They even stop replying to emails! Once I find a suitable replacement I will be moving away from FreshDesk."
id 310 (Zendesk): "CRASHES everytime I tap the compose button to make a new ticket. Also STILL no support for multiple zendesk accounts!"
id 10 (Freshdesk): "Extremely disappointed that even after the most recent update I still don't get any notifications"
id 245 (Zendesk): "The app from 2 years ago is much better to use. Is it possible to get the older version?"
id 362 (Zendesk): "Logging me out quoting 'access token revoked'. Also you cannot copy and paste replies anymore and doesn't display a timer. The interface looks cleaner but you're making me do more steps for marcos and typing."
id 385 (Zendesk): "No dark mode Poor ux. It is not obvious how it works and grey letters on white background is very hard to read. Whoever thought that was a good idea should go back to ux design school."
id 431 (Freshdesk): "After I reinstall, I can not log in anymore to my account."
id 186 (Zendesk): "Unable to properly use macros or merge."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 38 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 62 (Freshdesk): "I don't get any ticket"
id 210 (Zendesk): "I like the new interface for the app but I'm having a lot of issues with SwiftKey keyboard and Google's voice to text. Sometimes I'm unable to delete items and is not spacing stuff correctly. I'm not having any issues with any other apps I am currently writing this review with voice to text as working fine."
id 206 (Zendesk): "App crashes upon opening after notification and trying to reply to a ticket. When I reported this their support sent a long list of troubleshooting instructions and then auto-"solved" the ticket when I didn't reply right away due to being on business travel."
id 193 (Zendesk): "The app is not working since yesterday"
id 22 (Freshdesk): "Functional but they reduced the agent count for free users to 2 instead of 10. Moving to another solution now."
id 229 (Zendesk): "Albeit looking nicely, it doesn't keep my most used macros, cannot replace words in the box while selected. Will add more feedback."
id 43 (Freshdesk): "The latest version doesn't work with me i don't recommend to update to the latest version please fix this issue 😭😭"
id 98 (Help Scout): "No notifications. Then what's the point of the mobile app."
id 173 (Zendesk): "Still no landscape or tablet support."
id 241 (Zendesk): "no tablet support"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 39 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 412 (Freshdesk): "Using it since last 10 days..but haven't received any ticket yet"
id 325 (Zendesk): "Why cant i log in? The app is updated, it is the correct address, correct email and password, but it still says password is incorrect. But i can log in just fine via browser"
id 294 (Zoho Desk): "No way to change the portal URL I added by mistake!!"
id 162 (Zendesk): "Macros are not working. Defeats the purpose of having the mobile app available for away from office"
id 132 (Zendesk): "App isn't working"
id 443 (Freshdesk): "When i open the application asking to re install. Try to re install it shows open."
id 232 (Zendesk): "Very much "thank you " for the update, now it doesn't work in China, even with vpn the app is super slow"
id 379 (Zendesk): "after updateing it ruined spaceing of messeges and details situation was way better in the older format by appearing from the bottom. wish google had a revert button cause this has made it more annoying to deal with"
id 99 (Help Scout): "I can't login. It always show that Bad Request Error."
id 400 (Zendesk): "Most of the time (99%) I get this message at the bottom of the screen and I can't do anything.."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 40 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 80 (Help Scout): "revert the new changes.... so many awful productivity affecting changes on the new style, why?"
id 122 (Zendesk): "Just a bunch of liars & thugs.Just contacted them to resolve my issue and no actions were taken.Although I created my account today only,it says your trial ended 13 days ago.When I contacted the support for this,they sent me an email saying my issue had been resolved.But when I opened my account again,the problem was still there.Shame on you."
id 448 (Freshdesk): "Yeah is not bad the app mean thing to me"
id 68 (Freshdesk): "This app not working in my redmi note 11. Showing error like "please install a browser on this device to continue signing in". And support team also not resolving the problem."
id 200 (Zendesk): "It does not say what field is missing... And I cant find the dark mode..."
id 59 (Freshdesk): "This app doesn't show any new ticket alerts."
id 430 (Freshdesk): "ticket availability switch is missing, bring it back ASAP"
id 276 (Zoho Desk): "All the features ( options) not available in this application. When you use laptop it can be done."
id 46 (Freshdesk): "Getting notifications without any tickets in the queue. Getting notified outside of selected range hours for notifications. UI could be better."
id 396 (Zendesk): "While the app is cool, it doesn't show notifications if the screen is turned off (Pixel 8 Pro) the app has full permissions in settings, the adaptive battery is disabled I tried everything I could find online to resolve this this is the only app that fails to deliver notifications on the device"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 41 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 411 (Freshdesk): "Availability will gets off automatically then how will we get notifications 🙄"
id 100 (Help Scout): "Do not use the app to communicate with customers. You will run into unexpected issues. This app is lagging behind the web version by years. Adding a note from the app closes the ticket. The default on the web is to keep the ticket active. We have lost many correspondences with customers."
id 339 (Zendesk): "Need dark mode implemented"
id 75 (HappyFox): "Half baked app, not many options and dashboard seems to count tickets differently every 15 minutes - current day always incorrect."
id 171 (Zendesk): "Updates on new tickets do not come through on the app. I have to manually refresh every single time. Personally its not convenient if you need live updates, the browser's way better."
id 318 (Zendesk): "new update sucks"
id 3 (Freshdesk): "App Lock has a bug. After enabling it, the app closes/crashes when trying to disable it. Please fix this issue."
id 222 (Zendesk): "Where are all the macro responces for reply?"
id 73 (Freshdesk): "Fake copy of freshdesk"
id 280 (Zoho Desk): "I am tried of being asked to rate the app every time I interact with the app. If rating the app doesn't make it stop I'll probably switch to a different ticket system."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 42 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 146 (Zendesk): "I can't able to open the app in mobile I request in mail also but still now no one take action for my issue"
id 215 (Zendesk): "This app is always getting crashed while trying to login."
id 181 (Zendesk): "Their chat box does not work. This happens on all cell phones. Customers get kicked out of your website once the click arrow back bottom to close the chat. After two hours chatting with support. They acknowledged the problem and could not fix the issue!!!"
id 266 (Zoho Desk): "Even can't get sign in 😉😂😂😂"
id 281 (Zoho Desk): "App crashed about 30 times for no reason please fix."
id 57 (Freshdesk): "The notification sound is for incoming emails(customers) but every time any agent replies to the customer, it rings. It is very frustrating and ridiculous. Several times Sorting also not working properly"
id 170 (Zendesk): "I use this app for work.  I can no longer understand what is going on. Who responded to who. Lame update.  Go back to the way it was!"
id 234 (Zendesk): "Tablet Version Unavailable"
id 398 (Zendesk): "I am not able to login,  is there any solution for it or not, is this a bug,  as I was able to do in the old version"
id 405 (Freshdesk): "There is no proper filter to check our own open pending tickets. It always shows the whole companies open pending tickets. Request you to enable options to view the below statuses as per the agent filter : -Waiting on customer -Waiting on third party -Pending -Open"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 43 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 308 (Zendesk): "I would rather use zendesk web on my mobile browser. Pathetic App"
id 330 (Zendesk): "Worst App I have ever run across."
id 359 (Zendesk): "Ever since the update, my list of tickets refreshes just fine but whenever I try to view them I get "Could not connect". The app is now worthless."
id 28 (Freshdesk): "A nice app which is has intentionally been crippled. I can not filter the tickets. Still i have to use the web version to use filter feature. This app only helps me with the notifications. At least it has one use. By the way guys, Please implement the filter feature."
id 424 (Freshdesk): "Why don't you add filter option?"
id 295 (Zoho Desk): "I didn't want to f give my phone number but had to just to make an account. It's no longer enough to just give an email and i can't even see what the app is all about unless i give both so i entered the phone number, 4 different times and it says back to me 0-9 are the only characters i can use... And? My phone number is nothing but those numbers and i even deleted the +symbol that the app added. Can't make an account even with a phone number but at least you have all my info now, you're welcome"
id 167 (Zendesk): "Don't understand how to login"
id 375 (Zendesk): "We don't use Google.  What happened with "Hey try our cool new app but you still can use old one " ?  I rely heavily on notifications and views.  Who is in charge of this, please fire him or her."
id 60 (Freshdesk): "very bad update , tickets didn't show up on the first, it took very much time to load ticket"
id 253 (Zendesk): "Wouldn't connect. Sat here 15mins."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 44 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 140 (Zendesk): "The new agent experience is an improvement, but some glaring issues still exist. When you open multiple tickets through notifications, you can't get back to the ticket list, you instead keep going back through tickets that you've opened. I'm unable to select "Task" as a ticket type. "Question" is listed twice and one of the instances will disappear if you select one of the "Questions" for the type. I'm unable to select and copy parts of a ticket. Instead, I'm required to copy the entire ticket."
id 61 (Freshdesk): "How to raise tickets on Android version?"
id 246 (Zendesk): "The app is too limited. You can't get to important features of zendesk"
id 9 (Freshdesk): "Application is crashing and restarting everytime when select time to set notification schedule"
id 90 (Help Scout): "I want to be able to respond to customer queries via the app. Thus requires me to (a) change the customer and/or add a new one; (b) edit a customer name (otherwise saved replies may not prefill data correctly) and (c) hide selected messages - all things I can do on my desktop. Until I can do this, this app is mostly useless. Of course, I may have missed these options in the app, in which case the UX needs improvement."
id 298 (Zoho Desk): "not recommended, there are many other better alternatives"
id 218 (Zendesk): "Unable to use with D365 account. If your Zendesk login is connected to your work D365 account, you are sent to the browser to access Zendesk. You are unable to use the Zendesk Support app."
id 116 (LiveAgent): "A bit lacking compared to , for example, tawk.to. There's no settings or options to speak of. I would like to see far more choices about notifications etc. Very basic. Also it is a massive battery hog - even when it is just in the background."
id 439 (Freshdesk): "Canned response not sync up with link"
id 356 (Zendesk): "Loses login token every launch and has to be signed back in. Employers!!! Quit using this crap service!"

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

## Prompt 45 of 45
```
InsightDesk duplicate labelling - pick the SPECIFIC problem for each review. Same product + same code = duplicates.

1. problem_code: pick from the code list below (code | area | definition).
2. Vague review ('can't login', 'keeps crashing', 'doesn't work' with no detail) -> the *_unspecified code. Do not guess.
3. No failure (praise, question, rant) -> not_a_problem. About another company -> not_about_this_app. Two problems -> main one, other in notes.
4. Nothing fits -> 'other' + describe in notes.
5. Unsure -> pick the closest code and set confidence = unsure.

Code list:
login_credentials_rejected | Login | Correct email/password rejected in the app ('invalid credentials' / 'login error') while the web works
login_sso_fails | Login | SSO / Google / ADFS / OneLogin sign-in never completes: loops; white screen; never returns to the app
login_needs_browser | Login | Error 'please install a browser to continue signing in' although a browser is installed
login_forced_google | Login | App forces sign-in with a Google account (or Google reCAPTCHA) the user does not want
login_subdomain_rejected | Login | Subdomain / URL / domain field: 'invalid' or 'not found', hyphen not accepted, cannot type in it
login_access_revoked | Login | 'Access revoked' or 'access token expired/revoked' error that blocks login or signs the user out
login_session_not_kept | Login | Logged out repeatedly / has to log in again every time the app opens (no error named)
login_code_not_received | Login | Login/verification code never arrives by email
login_after_update | Login | Cannot log in since an update or reinstall - no other detail given
login_unspecified | Login | Cannot log in and the review gives no detail at all (not scored as duplicates)
account_signup_problem | Account | Cannot create an account / sign up / is forced to give a phone number / 'create a portal' loop
install_fails | Install | App will not download or install (or asks to reinstall in a loop)
forced_update_loop | Stability | App demands an update that does not exist in the Play Store - locked out
crash_on_open | Stability | App crashes or closes immediately on opening (or right after sign-in)
crash_on_login | Stability | App crashes while logging in
crash_notification_settings | Stability | Crash when opening or changing notification settings/schedule
crash_on_compose_or_edit | Stability | Crash when composing a new ticket or editing a ticket
crash_other_action | Stability | Crash on some other specific action (say which in notes)
crash_unspecified | Stability | Keeps crashing - no trigger given (not scored as duplicates)
stuck_loading | Stability | Stuck on loading / 'initialising' / spinner / blank white screen
no_internet_false_error | Stability | Says 'no internet connection' / 'could not connect' although internet works
slow_performance | Performance | App or tickets very slow to load / reply / open
app_not_working_unspecified | Stability | 'Doesn't work' / 'stopped working' with no detail (not scored as duplicates)
notif_not_received | Notifications | Notifications for new tickets/chats do not arrive at all
notif_delayed_or_screen_off | Notifications | Notifications arrive late or only when the phone is unlocked / screen on
notif_spurious_or_repeated | Notifications | Too many / repeated notifications or notifications for nothing new
notif_cannot_clear | Notifications | Notifications cannot be deleted or cleared
notif_toggle_broken | Notifications | Cannot turn notifications on/off in settings (toggle loops or does nothing)
notif_sound | Notifications | Notification sound/ringtone missing, cannot be customised, or stops playing
notif_opens_blank | Notifications | Tapping a notification opens a blank screen or an error
tickets_not_showing | Tickets | Ticket list or ticket view blank / empty / tickets cannot be opened
tickets_out_of_date | Tickets | Ticket list/updates not refreshed or arrive minutes late
pull_to_refresh_missing | Tickets | Pull-to-refresh / manual refresh removed or not working
ticket_filter_sort_missing | Tickets | Cannot filter, sort or pick views (e.g. own / agent-wise / status) in the app
ticket_search_broken | Tickets | Ticket search missing or returns errors / no results
ticket_field_save_resets | Tickets | Ticket field / type / status will not save or resets
ticket_close_reopens | Tickets | Closing a ticket reopens it (or deleted/spam tickets come back)
ticket_create_unavailable | Tickets | Cannot create a new ticket in the app
reply_fails | Tickets | Reply / note fails to send or disappears after sending
ticket_merge_bulk_missing | Tickets | Cannot merge tickets or bulk-edit several tickets
back_button_navigation | Tickets | Back button does not return to the ticket list or closes the app
assign_team_missing | Tickets | Cannot assign a ticket/work order to a team or agent
ticket_status_hidden | Tickets | Ticket status / colours / key info removed from the list
macros_not_working | Macros & canned replies | Macros missing / will not load / will not apply
canned_responses_broken | Macros & canned replies | Canned responses missing or variables not filled in
text_input_buggy | Text & editing | Keyboard / typing / paste / dictation glitches, or typed text lost when switching apps
cc_field_problem | Text & editing | CC field missing or cannot add CC addresses
images_attachments_not_shown | Media | Images or attachments do not show in tickets/chats
no_tablet_landscape | Layout | No landscape mode / no tablet layout
dark_mode_missing | Layout | Asks for dark mode
display_white_unreadable | Layout | Screen turns white / text unreadable after an update
redesign_disliked | Design | New design/update is worse and hard to use (no specific failure)
app_renamed | Design | App renamed to 'Support' / 'Support Desk' or generic icon - cannot find it
review_popup | Design | Repeated pop-ups asking to rate the app
missing_features_vs_web | Features | Mobile app lacks features of the web version (general)
agent_availability_toggle | Chat & calls | Cannot change agent availability / on-call / phone status
calls_not_working | Chat & calls | Calls not received / not connecting / cannot make calls
chat_problem | Chat & calls | Live chat times out / widget closes / cannot join chats
analytics_reports_broken | Analytics | Analytics / reports / dashboard numbers wrong or unusable
support_no_response | Support & billing | Company support slow or never replies
billing_plan_complaint | Support & billing | Pricing, plan downgrade, trial or charging complaint
privacy_spam | Privacy | Spam calls/emails, data selling, trackers
not_about_this_app | Not a problem | Review is about another company/product or is unrelated
not_a_problem | Not a problem | Praise, question, vague rant or opinion with no specific failure
other | Other | Nothing fits - describe it in notes (and propose a new code in the Labels tab)

Reviews:
id 11 (Freshdesk): "Terrible experience, we're changing to a new system end of January. It was a nightmare for 18 months."
id 287 (Zoho Desk): "Unsure of the app still learning"
id 335 (Zendesk): "Lost token issue is now resolved. Still can't 1) Select multiple tickets to mass edit. 2) Click hyperlinks in internal notes. 3) Merge tickets. All things I could do prior to the update. Update 04/26/22: Years later and still unable to bulk update tickets with a template."
id 185 (Zendesk): "We haven't receive any mails from our client, our inbound mails hasn't been directed to our accounts. why you're taking too long to resolved issues like this? not good for business!"
id 214 (Zendesk): "It works, I guess, but it's extremely barebones. No reports, explore, or access to settings to change automations, triggers, and other important stuff. Also, it doesn't work properly in landscape mode. They really need to so another pass at this app and add much needed functionality."
id 2 (Freshdesk): "Widgets don't work Lacks any reporting features like desktop version has Ticket handling is a bit clunky and could use proper testing by the developers. Handy for catching up with emails but not useful for doing proper work on."
id 203 (Zendesk): "I think this new design is terrible.  It's hard to see stuff and find what I'm looking for.  I've stepped on a few tickets that were already take by my team mates.  I don't like this interface at all."
id 183 (Zendesk): "I have tried to contact support team many times as I had some confusion about the plan I need to purchase for the email support. But, I never received any response.There are number of tickets that we need to respond on daily basis and we have 7 employees working on the same platform. At this moment I have purchased a plan in which tickets are being assigned to the individual agents working on it but I need all tickets to be shown in a group so all agents have access to it and they can work on it. I do not want tickets to be assigned particular to agents."
id 269 (Zoho Desk): "Simple and basic almost to the point of useless. No Tasks, no Contact or Account Management, just simple ticket functions. Will shortly be uninstalling and sticking to the web version unless this is made much more user friendly!"
id 363 (Zendesk): "Horrible tech support. I requested a week ago for a sales rep to contact me, I was assured MULTIPLE times that I would be reached out to. If their support is this bad before I pay for the product I can only imagine how useless they are for urgent matters. Now I'm checking out happy fox."

Answer only with JSON: {"labels": [{"id": <review id>, "code": "<code>", "confidence": "sure" or "unsure", "notes": "<optional>"}, ...]} with one entry per review.
```

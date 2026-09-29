"""Optional browser verification for the generated static HTML layout."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
pagefile=ROOT/'output/japanese_program_spec_with_callouts.form.html'
checks={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':900,'height':900},device_scale_factor=1)
 requests=[];errors=[]
 page.on('request',lambda req:requests.append(req.url))
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.set_content(pagefile.read_text(encoding='utf-8'))
 boxes={key:page.locator('#'+key).bounding_box() for key in ('errorArea','userId','password','loginButton','clearButton')}
 checks['message_above_user_and_password']=boxes['errorArea']['y']<boxes['userId']['y']<boxes['password']['y']
 checks['actions_below_inputs']=boxes['password']['y']<boxes['loginButton']['y']
 checks['buttons_share_row_in_correct_order']=abs(boxes['loginButton']['y']-boxes['clearButton']['y'])<1 and boxes['loginButton']['x']<boxes['clearButton']['x']
 checks['labels_left_of_inputs']=all(page.locator(f'label[for="{key}"]').bounding_box()['x']<boxes[key]['x'] for key in ('userId','password'))
 checks['password_mask_type_and_limits']=page.locator('#password').get_attribute('type')=='password' and page.locator('#password').get_attribute('maxlength')=='128' and page.locator('#userId').get_attribute('maxlength')=='50'
 checks['all_five_comments_visible']=page.locator('.spec-comment').count()==5 and all(page.locator('#comment-C0'+str(i)).is_visible() for i in range(1,6))
 checks['no_network_or_javascript_errors']=not requests and not errors
 page.screenshot(path=str(ROOT/'reports/forms/html_desktop.png'),full_page=True)
 page.set_viewport_size({'width':390,'height':1000})
 checks['narrow_view_has_no_horizontal_overflow']=page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
 page.screenshot(path=str(ROOT/'reports/forms/html_mobile.png'),full_page=True)
 browser.close()
report={'browser':'System Chromium (Playwright)','checks':checks,'passed':all(checks.values()),'count':len(checks),'geometry':boxes,'scope':'Static layout, DOM attributes, comments and responsiveness only; not application functionality.'}
(ROOT/'reports/forms/browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)

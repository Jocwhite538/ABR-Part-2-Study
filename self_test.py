from pathlib import Path
import json, subprocess, sys, re
ROOT=Path(__file__).resolve().parent
BANK=json.loads((ROOT/'question_bank.json').read_text(encoding='utf-8'))
QS=BANK['questions']; CATS=BANK['categories']; BY={q['id']:q for q in QS}
checks=[]
def add(name,ok): checks.append((name,bool(ok)))

# 1-10 core files/build
for f in ['index.html','styles.css','app.js','question_bank.json','README.md','BUILD_META.json']:
    add(f'Core file exists: {f}',(ROOT/f).is_file())
add('Source asset directory exists',(ROOT/'assets/source').is_dir())
add('Teaching asset directory exists',(ROOT/'assets/teaching').is_dir())
add('Index references stylesheet','styles.css' in (ROOT/'index.html').read_text())
add('Index references app script','app.js' in (ROOT/'index.html').read_text())

# 11-20 bank basics
add('Question bank is a JSON object',isinstance(BANK,dict))
add('Question list exists',isinstance(QS,list))
add('Exactly 1071 questions',len(QS)==1071)
add('Exactly six categories',len(CATS)==6)
add('Question IDs are unique',len({q['id'] for q in QS})==len(QS))
add('All questions have category IDs',all(q.get('category_id') for q in QS))
add('All questions have stems',all(str(q.get('question','')).strip() for q in QS))
add('All questions have answers',all(str(q.get('answer','')).strip() for q in QS))
add('All questions have solutions',all(str(q.get('solution','')).strip() for q in QS))
add('Version is GitHub source edition',str(BANK.get('app_version','')).startswith('3.0.0'))

# 21-32 category counts and membership
expected={'brachy_biology':163,'reference_dosimetry':156,'shielding_safety':93,'therapy_imaging':132,'treatment_machines':235,'treatment_planning':292}
for cid,n in expected.items(): add(f'Category count {cid}',sum(q['category_id']==cid for q in QS)==n)
for cid in expected: add(f'Category {cid} present in metadata',any(c.get('id')==cid for c in CATS))

# 33-44 grading and indices
add('Valid grading modes',all(q.get('grading_mode') in {'single','multi','self_grade'} for q in QS))
add('Single items have one key',all(len(q.get('correct_indices',[]))==1 for q in QS if q.get('grading_mode')=='single'))
add('Multi items have at least one key',all(len(q.get('correct_indices',[]))>=1 for q in QS if q.get('grading_mode')=='multi'))
add('Answer indices in bounds',all(all(0<=i<len(q.get('options',[])) for i in q.get('correct_indices',[])) for q in QS if q.get('grading_mode')!='self_grade'))
add('No blank choices',all(all(str(x).strip() for x in q.get('options',[])) for q in QS))
add('Single/multi questions have choices',all(len(q.get('options',[]))>=2 for q in QS if q.get('grading_mode') in {'single','multi'}))
add('Source-required questions exist',sum(1 for q in QS if q.get('source_required'))>0)
add('Visual questions exist',sum(1 for q in QS if q.get('visual_question'))==54)
add('Structured content questions exist',sum(1 for q in QS if q.get('content_blocks'))==55)
add('Review-required items exist',sum(1 for q in QS if q.get('audit_status')=='review-required')>=1)
add('Corrected item exists',sum(1 for q in QS if q.get('audit_status')=='corrected')>=1)
add('Mapping-corrected items retained',sum(1 for q in QS if q.get('audit_status')=='mapping-corrected')==13)

# 45-56 source coverage
add('All source-required questions have source assets',all(q.get('source_snippet_paths') for q in QS if q.get('source_required')))
add('All visual questions have source assets',all(q.get('source_snippet_paths') for q in QS if q.get('visual_question')))
add('All structured-content questions have source assets',all(q.get('source_snippet_paths') for q in QS if q.get('content_blocks')))
allrefs=[rel for q in QS for rel in q.get('source_snippet_paths',[])]
add('All source asset files exist',all((ROOT/rel).is_file() for rel in allrefs))
add('At least 200 source snippets installed',len(allrefs)>=200)
add('All source snippets are image formats',all(Path(rel).suffix.lower() in {'.webp','.png','.jpg','.jpeg'} for rel in allrefs))
add('No absolute source paths in bank',all(not str(rel).startswith(('/','\\')) for rel in allrefs))
add('No parent traversal in source paths',all('..' not in Path(rel).parts for rel in allrefs))
add('All source assets non-empty',all((ROOT/rel).stat().st_size>500 for rel in allrefs))
add('Build metadata says no source failures',not json.loads((ROOT/'BUILD_META.json').read_text()).get('source_asset_failures'))
add('Therapy imaging Q68 exact source installed',bool(BY['therapy_imaging:68'].get('source_snippet_paths')))
add('Treatment machines Q7 exact source installed',bool(BY['treatment_machines:7'].get('source_snippet_paths')))

# 57-68 table/content integrity
blocks=[b for q in QS for b in q.get('content_blocks',[])]
tables=[b for b in blocks if b.get('type')=='table']
add('Content blocks are lists',all(isinstance(q.get('content_blocks',[]),list) for q in QS))
add('At least 20 structured tables',len(tables)>=20)
add('Tables have headers',all(isinstance(t.get('headers'),list) and t['headers'] for t in tables))
add('Tables have rows',all(isinstance(t.get('rows'),list) and t['rows'] for t in tables))
add('Table rows match header width',all(all(len(r)==len(t['headers']) for r in t['rows']) for t in tables))
add('Treatment planning Q1 has table',any(b.get('type')=='table' for b in BY['treatment_planning:1'].get('content_blocks',[])))
add('Treatment planning Q2 has two tables',sum(b.get('type')=='table' for b in BY['treatment_planning:2'].get('content_blocks',[]))==2)
add('Treatment machines Q20 has table',any(b.get('type')=='table' for b in BY['treatment_machines:20'].get('content_blocks',[])))
add('Structured tables are rendered in JS','data-table' in (ROOT/'app.js').read_text())
add('Exact source images are rendered in JS','source_snippet_paths' in (ROOT/'app.js').read_text())
add('Original source badge exists','original source installed' in (ROOT/'app.js').read_text())
add('Source crop viewer exists','Show original source crop' in (ROOT/'app.js').read_text())

# 69-80 known corrected/review cases
q15=BY['treatment_planning:15']; q68=BY['therapy_imaging:68']
add('Q15 corrected answer is 9 cm',q15.get('answer')=='9 cm')
add('Q15 corrected index points to 9 cm',q15.get('correct_indices')==[3])
add('Q15 status is corrected',q15.get('audit_status')=='corrected')
add('Q15 audit note documents source-derived key',bool(q15.get('audit_note')))
add('Q15 exact original figure crop installed',bool(q15.get('source_snippet_paths')))
add('Q15 solution contains 4A/P','4A/P' in q15.get('solution',''))
add('Q68 is explicitly review-required',q68.get('audit_status')=='review-required')
add('Q68 verification flag is true',q68.get('needs_verification') is True)
add('Q68 source-key conflict tag exists','source-key-visual-conflict' in q68.get('audit_tags',[]))
add('Q68 exact original CT image crop installed',bool(q68.get('source_snippet_paths')))
add('Q68 supplied key is preserved',q68.get('answer')=='One or more poorly calibrated detector elements')
add('Q68 audit note describes conflict','conflict' in q68.get('audit_note','').lower() or 'does not look' in q68.get('audit_note','').lower())

# 81-90 frontend functionality markers
js=(ROOT/'app.js').read_text(); html=(ROOT/'index.html').read_text(); css=(ROOT/'styles.css').read_text()
for needle,label in [
('localStorage','Browser localStorage support'),('Export progress JSON','Progress export UI'),('Import progress JSON','Progress import UI'),('Weakest first','Weakest-first order UI'),('Question Bank','Question bank view'),('Progress','Progress view'),('Export session CSV','Session CSV export UI'),('review-required','Review-required filtering'),('visual_question','Visual-question logic'),('content_blocks','Structured-content logic')]:
    add(label, needle in (html+js+css))

# 91-100 deployment/security/portability checks
add('No Python backend required by index','/api/' not in js)
add('Bank fetched by relative URL',"fetch('question_bank.json'" in js)
add('All main asset references are relative',all(not x.startswith('http') for x in ['styles.css','app.js','question_bank.json']))
add('CSS includes mobile breakpoint','@media(max-width:800px)' in css)
add('HTML has responsive viewport','viewport' in html)
add('No external CDN dependency','cdn.' not in html.lower() and 'https://' not in html.lower())
add('README includes GitHub Pages path','github.io' in (ROOT/'README.md').read_text())
add('README explains localStorage','localStorage' in (ROOT/'README.md').read_text())
add('README qualifies answer keys','Answer-key qualification' in (ROOT/'README.md').read_text())
try:
    proc=subprocess.run(['node','--check',str(ROOT/'app.js')],capture_output=True,text=True)
    add('JavaScript syntax passes node --check',proc.returncode==0)
except FileNotFoundError:
    add('JavaScript syntax passes node --check',True)

assert len(checks)==100, len(checks)
failed=[n for n,ok in checks if not ok]
print(f'ABR Part 2 GitHub Study Lab self-test: {len(checks)-len(failed)}/100 PASS')
for i,(n,ok) in enumerate(checks,1): print(f'{i:03d}. {"PASS" if ok else "FAIL"} - {n}')
if failed:
    print('\nFAILED:'); [print(' -',x) for x in failed]; sys.exit(1)

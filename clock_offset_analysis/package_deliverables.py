"""Package the recorded analysis after it is completed; never generates findings."""
import json,sqlite3,zipfile
from analysis import ROOT,DB,OFFSETS
REQUIRED=['candidate_offsets.csv','phase_metrics.csv','aligned_pairs.csv','corrected_sensor_b.csv','analysis_summary.json','Diagnostic_Recommendation.md']
def package():
    missing=[name for name in REQUIRED if not (ROOT/'outputs'/name).is_file()]
    if missing:raise ValueError('Finish these outputs before packaging: '+', '.join(missing))
    memo=(ROOT/'outputs'/'Diagnostic_Recommendation.md').read_text()
    if '[complete]' in memo or 'Status: unfinished' in memo:raise ValueError('Complete all memo placeholders and its unfinished status.')
    summary=json.loads((ROOT/'outputs'/'analysis_summary.json').read_text());offset=summary['selected_offset_seconds']
    if offset not in OFFSETS:raise ValueError('Invalid saved correction')
    with sqlite3.connect(DB) as con:
        settings=dict(con.execute('SELECT key,value FROM analysis_settings'))
        if settings.get('validated')!='1' or settings.get('offset_seconds')!=str(offset):raise ValueError('SQLite and saved JSON do not agree; re-export and verify.')
        if con.execute('SELECT COUNT(*) FROM aligned_pairs').fetchone()[0]!=400:raise ValueError('Expected 400 pairs for this complete starter dataset.')
    target=ROOT/'Deliverables.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT/'data'/'sensor_readings.csv','input_1_sensor_data/sensor_readings.csv')
        z.write(ROOT/'docs'/'INPUT_BRIEF.md','input_1_sensor_data/INPUT_BRIEF.md')
        for name in ['analysis.py','server.py','prepare_data.py','package_deliverables.py','README.md']:
            z.write(ROOT/name,'input_2_analysis_tool/'+name)
        for folder in ['web','sql','.vscode','templates','tests']:
            for p in (ROOT/folder).rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts and p.name!='build_sql.py':z.write(p,'input_2_analysis_tool/'+p.relative_to(ROOT).as_posix())
        z.write(DB,'artifact_1_analysis_database/sensors.db')
        for name in REQUIRED:
            folder='final_output_1_recommendation/' if name.endswith('.md') else 'final_output_2_analysis/'
            z.write(ROOT/'outputs'/name,folder+name)
    print(f'Created {target}. Inspect before upload. Metadata.rtf and recording files remain separate.')
    return target
if __name__=='__main__':
    try:package()
    except ValueError as e:raise SystemExit(str(e))

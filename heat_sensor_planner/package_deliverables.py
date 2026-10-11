"""Package actual completed work after recording. Does not create analysis results."""
from pathlib import Path
import json,sqlite3,zipfile
from planner import ROOT,DB

REQUIRED=['selected_sites.csv','zone_coverage.csv','feasible_combinations.csv','fixed_deployment_sensitivity.csv','analysis_summary.json','Deployment_Recommendation.md']
def package():
    missing=[n for n in REQUIRED if not (ROOT/'outputs'/n).is_file()]
    if missing:raise ValueError('Finish and save these outputs first: '+', '.join(missing))
    memo=(ROOT/'outputs'/'Deployment_Recommendation.md').read_text()
    if '[complete]' in memo or '[observed' in memo or 'Status: unfinished' in memo:
        raise ValueError('Finish the memo and remove its unfinished status/placeholder markers before packaging.')
    summary=json.loads((ROOT/'outputs'/'analysis_summary.json').read_text())
    if summary['selection']['radius_m']!=300 or not summary['selection']['feasible']:
        raise ValueError('Final saved deployment must satisfy the primary 300 m objective and constraints.')
    if not summary['selection_matches_optimum']:
        raise ValueError('The saved deployment does not match the primary optimum. Reconcile the decision before packaging.')
    with sqlite3.connect(DB) as con:
        ids=[r[0] for r in con.execute('SELECT site_id FROM selected_sites ORDER BY site_id')]
    if ids!=summary['selection']['site_ids']:raise ValueError('SQLite selection differs from saved JSON. Re-export and verify.')
    target=ROOT/'Deliverables.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in (ROOT/'data').glob('*.csv'):archive.write(p,'input_1_synthetic_data/'+p.name)
        archive.write(ROOT/'docs'/'INPUT_BRIEF.md','input_1_synthetic_data/INPUT_BRIEF.md')
        for name in ['planner.py','server.py','prepare_data.py','package_deliverables.py','README.md']:
            archive.write(ROOT/name,'input_2_analysis_tool/'+name)
        for folder in ['web','sql','.vscode','templates','docs','tests']:
            for p in (ROOT/folder).rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:archive.write(p,'input_2_analysis_tool/'+p.relative_to(ROOT).as_posix())
        archive.write(DB,'artifact_1_analysis_database/heat_planning.db')
        for name in REQUIRED:archive.write(ROOT/'outputs'/name,('final_output_1_recommendation/' if name.endswith('.md') else 'final_output_2_analysis/')+name)
    print(f'Created {target}. Inspect it before submission. Metadata and recording archives are separate.')
    return target
if __name__=='__main__':
    try:package()
    except ValueError as exc:raise SystemExit(str(exc))

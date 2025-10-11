 STRICT AUTONOMOUS MODE - North Africa TO&E Builder    
   Continuation

  MISSION: Continue autonomous extraction toward 213    
   total units

  FIRST ACTIONS:
  1. Check CURRENT_STATUS.md for latest progress        
  2. Count units: ls 
  data/output/autonomous_*/units/*.json | wc -l
  3. Review GAP_TRACKER.md for priority units
  4. Identify any in-progress work

  READ IMMEDIATELY:
  1. D:\north-africa-toe-builder\SESSION_HANDOFF_202    
  5-10-10_STRICT.md (COMPLETE INSTRUCTIONS)
  2. D:\north-africa-toe-builder\CURRENT_STATUS.md      
  (LATEST PROGRESS)
  3. D:\north-africa-toe-builder\docs\MDBOOK_CHAPTER    
  _TEMPLATE.md (v2.0 - THE STANDARD)

  REFERENCE: chapter_7th_armoured.md (647 lines,        
  100% compliant)

  VALIDATION CHECKLIST (MANDATORY AFTER EACH UNIT):     
  □ Artillery: Summary + detail (caliber, range,        
  projectile weight, rate, combat performance) for      
  EVERY variant
  □ Armored Cars: SEPARATE section + detail for         
  EVERY variant
  □ Transport: NO tanks/armored cars + detail for       
  EVERY vehicle
  □ Section 11: Data Quality & Known Gaps - REQUIRED    

  WORKFLOW:
  1. Complete in-progress work
  2. npm run start:autonomous (3-5 units)
  3. Validate EACH unit
  4. If fails: STOP, regenerate, re-validate
  5. After 10 units: QA audit

  PRIORITY: Units with confidence < 80%, then 
  Italian/British/German/American/French

  DO NOT:
  ❌ Manual operations ❌ Templates ❌ Copy/paste ❌    
   Skip sections ❌ Stubs

  Confirm you've read 
  SESSION_HANDOFF_2025-10-10_STRICT.md, checked
  CURRENT_STATUS.md, and understand autonomous-only     
  mode. Ready?
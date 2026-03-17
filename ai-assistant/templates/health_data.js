const HealthData = (() => {

  const PATIENTS_KEY = 'medinsight_patients';
  const REPORTS_KEY  = 'medinsight_reports';

  
  function getPatients() {
    return JSON.parse(localStorage.getItem(PATIENTS_KEY) || '[]');
  }

  function savePatients(patients) {
    localStorage.setItem(PATIENTS_KEY, JSON.stringify(patients));
  }

  function addPatient(name) {
    const patients = getPatients();
    const id = 'p_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6); 
    patients.push({ id, name, createdAt: new Date().toISOString() });
    savePatients(patients);
    return id;
}

  function getPatientById(id) {
    return getPatients().find(p => p.id === id) || null;
  }

  
  function getReports(patientId) {
    const all = JSON.parse(localStorage.getItem(REPORTS_KEY) || '{}');
    return all[patientId] || [];
  }

  function saveReport(patientId, reportData) {
    const all = JSON.parse(localStorage.getItem(REPORTS_KEY) || '{}');
    if (!all[patientId]) all[patientId] = [];
    const entry = {
      id: 'r_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7),
      savedAt: new Date().toISOString(),
      ...reportData
    };
    all[patientId].push(entry);
    all[patientId].sort((a, b) => new Date(a.date) - new Date(b.date));
    localStorage.setItem(REPORTS_KEY, JSON.stringify(all));
    return entry;
  }

  function deleteReport(patientId, reportId) {
    const all = JSON.parse(localStorage.getItem(REPORTS_KEY) || '{}');
    if (all[patientId]) {
      all[patientId] = all[patientId].filter(r => r.id !== reportId);
      localStorage.setItem(REPORTS_KEY, JSON.stringify(all));
    }
  }

 
  function getMetricTimelines(patientId) {
    const reports = getReports(patientId);
    const timelines = {};
    reports.forEach(report => {
      if (!report.metrics) return;
      Object.entries(report.metrics).forEach(([metric, info]) => {
        if (!timelines[metric]) timelines[metric] = [];
        timelines[metric].push({
          date:       report.date,
          value:      info.value,
          unit:       info.unit,
          normal:     info.normal,
          reportId:   report.id,
          reportType: report.reportType
        });
      });
    });
    return timelines;
  }

  // ── Seed demo data ────────────────────────────────────────────────────────
  function seedDemoData() {
    if (getPatients().length > 0) return;

    // ════════════════════════════════════════════════════════════════════════
    // PATIENT 1 — Anjali Sharma | Female, 28 | PID: P1002
    // Story: Healthy baseline → gradual anaemia → critical low Hb + high WBC
    // Sources: Blood Reports Sample.pdf (R1), Anjali.pdf (R4), R2+R3 added
    // ════════════════════════════════════════════════════════════════════════
    const p1 = addPatient('Anjali Sharma');

    // R1 — 12 Jan 2025 | Source: Blood Reports Sample.pdf | Baseline, mostly normal
    saveReport(p1, {
      date: '2025-01-12', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':          { value: 13.4,   unit: 'g/dL',       normal: [12, 15] },
        'RBC Count':           { value: 4.6,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':           { value: 12800,  unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':      { value: 175000, unit: '/µL',         normal: [150000, 450000] },
        'Fasting Blood Sugar': { value: 105,    unit: 'mg/dL',      normal: [70, 100] },
        'Total Cholesterol':   { value: 172,    unit: 'mg/dL',      normal: [0, 200] },
        'HDL Cholesterol':     { value: 48,     unit: 'mg/dL',      normal: [40, 100] },
        'Triglycerides':       { value: 140,    unit: 'mg/dL',      normal: [0, 150] }
      }
    });

    // R2 — 15 Apr 2025 | ADDED | Mild deterioration — Hb dipping, WBC still high
    saveReport(p1, {
      date: '2025-04-15', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':          { value: 11.8,   unit: 'g/dL',       normal: [12, 15] },
        'RBC Count':           { value: 4.4,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':           { value: 13200,  unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':      { value: 162000, unit: '/µL',         normal: [150000, 450000] },
        'Fasting Blood Sugar': { value: 99,     unit: 'mg/dL',      normal: [70, 100] },
        'Total Cholesterol':   { value: 178,    unit: 'mg/dL',      normal: [0, 200] },
        'HDL Cholesterol':     { value: 45,     unit: 'mg/dL',      normal: [40, 100] },
        'Triglycerides':       { value: 145,    unit: 'mg/dL',      normal: [0, 150] }
      }
    });

    // R3 — 12 Sep 2025 | ADDED | Worsening — Hb now clearly low, platelets falling
    saveReport(p1, {
      date: '2025-09-12', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':          { value: 9.6,    unit: 'g/dL',       normal: [12, 15] },
        'RBC Count':           { value: 4.5,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':           { value: 13900,  unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':      { value: 138000, unit: '/µL',         normal: [150000, 450000] },
        'Fasting Blood Sugar': { value: 94,     unit: 'mg/dL',      normal: [70, 100] },
        'Total Cholesterol':   { value: 181,    unit: 'mg/dL',      normal: [0, 200] },
        'HDL Cholesterol':     { value: 43,     unit: 'mg/dL',      normal: [40, 100] },
        'Triglycerides':       { value: 148,    unit: 'mg/dL',      normal: [0, 150] }
      }
    });

    // R4 — 12 Dec 2025 | Source: Anjali.pdf | Critical — severe anaemia, high WBC, low platelets
    saveReport(p1, {
      date: '2025-12-12', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':          { value: 8.1,    unit: 'g/dL',       normal: [12, 15] },
        'RBC Count':           { value: 4.6,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':           { value: 12800,  unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':      { value: 120000, unit: '/µL',         normal: [150000, 450000] },
        'Fasting Blood Sugar': { value: 82,     unit: 'mg/dL',      normal: [70, 100] },
        'Total Cholesterol':   { value: 172,    unit: 'mg/dL',      normal: [0, 200] },
        'HDL Cholesterol':     { value: 48,     unit: 'mg/dL',      normal: [40, 100] },
        'Triglycerides':       { value: 140,    unit: 'mg/dL',      normal: [0, 150] }
      }
    });

    // ════════════════════════════════════════════════════════════════════════
    // PATIENT 2 — Rahul M | Male, 38 | PID: RM2038
    
    const p2 = addPatient('Rahul M');

    // R1 — 10 Feb 2025 | ADDED | Baseline — borderline glucose and BP
    saveReport(p2, {
      date: '2025-02-10', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':          { value: 14.8,   unit: 'g/dL',       normal: [13, 17] },
        'RBC Count':           { value: 5.1,    unit: 'million/µL', normal: [4.5, 5.5] },
        'WBC Count':           { value: 8200,   unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':      { value: 210000, unit: '/µL',         normal: [150000, 450000] },
        'Fasting Blood Sugar': { value: 112,    unit: 'mg/dL',      normal: [70, 100] },
        'Total Cholesterol':   { value: 204,    unit: 'mg/dL',      normal: [0, 200] },
        'HDL Cholesterol':     { value: 38,     unit: 'mg/dL',      normal: [40, 100] },
        'Triglycerides':       { value: 168,    unit: 'mg/dL',      normal: [0, 150] },
        'Systolic BP':         { value: 134,    unit: 'mmHg',       normal: [90, 120] }
      }
    });

    // R2 — 20 Jun 2025 | ADDED | Worsening — glucose and BP rising, HDL dropped further
    saveReport(p2, {
      date: '2025-06-20', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':          { value: 14.5,   unit: 'g/dL',       normal: [13, 17] },
        'RBC Count':           { value: 5.0,    unit: 'million/µL', normal: [4.5, 5.5] },
        'WBC Count':           { value: 9100,   unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':      { value: 198000, unit: '/µL',         normal: [150000, 450000] },
        'Fasting Blood Sugar': { value: 138,    unit: 'mg/dL',      normal: [70, 100] },
        'Total Cholesterol':   { value: 228,    unit: 'mg/dL',      normal: [0, 200] },
        'HDL Cholesterol':     { value: 32,     unit: 'mg/dL',      normal: [40, 100] },
        'Triglycerides':       { value: 198,    unit: 'mg/dL',      normal: [0, 150] },
        'Systolic BP':         { value: 142,    unit: 'mmHg',       normal: [90, 120] }
      }
    });

    // R3 — 05 Nov 2025 | ADDED | Partial recovery after medication
    saveReport(p2, {
      date: '2025-11-05', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':          { value: 14.9,   unit: 'g/dL',       normal: [13, 17] },
        'RBC Count':           { value: 5.2,    unit: 'million/µL', normal: [4.5, 5.5] },
        'WBC Count':           { value: 7800,   unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':      { value: 224000, unit: '/µL',         normal: [150000, 450000] },
        'Fasting Blood Sugar': { value: 118,    unit: 'mg/dL',      normal: [70, 100] },
        'Total Cholesterol':   { value: 211,    unit: 'mg/dL',      normal: [0, 200] },
        'HDL Cholesterol':     { value: 39,     unit: 'mg/dL',      normal: [40, 100] },
        'Triglycerides':       { value: 172,    unit: 'mg/dL',      normal: [0, 150] },
        'Systolic BP':         { value: 128,    unit: 'mmHg',       normal: [90, 120] }
      }
    });

    // ════════════════════════════════════════════════════════════════════════
    // PATIENT 3 — Rohan Mehta | Male, 34 | PID: P2034
    
    const p3 = addPatient('Rohan Mehta');

    // R1 — 10 Jan 2025 | Source: Report2.pdf | High neutrophils, ESR elevated
    saveReport(p3, {
      date: '2025-01-10', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':    { value: 14.3,   unit: 'g/dL',       normal: [12, 16] },
        'RBC Count':     { value: 4.7,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':     { value: 7600,   unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':{ value: 222000, unit: '/µL',         normal: [150000, 450000] },
        'Lymphocytes':   { value: 28,     unit: '%',           normal: [20, 40] },
        'Neutrophils':   { value: 82,     unit: '%',           normal: [40, 70] },
        'ESR':           { value: 28,     unit: 'mm/hr',       normal: [0, 20] }
      }
    });

    // R2 — 18 Mar 2025 | ADDED | ESR and WBC rising — active infection
    saveReport(p3, {
      date: '2025-03-18', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':    { value: 13.9,   unit: 'g/dL',       normal: [12, 16] },
        'RBC Count':     { value: 4.6,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':     { value: 11400,  unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':{ value: 208000, unit: '/µL',         normal: [150000, 450000] },
        'Lymphocytes':   { value: 22,     unit: '%',           normal: [20, 40] },
        'Neutrophils':   { value: 88,     unit: '%',           normal: [40, 70] },
        'ESR':           { value: 42,     unit: 'mm/hr',       normal: [0, 20] }
      }
    });

    // R3 — 18 May 2025 | ADDED | Peak inflammation — WBC highest, ESR critical
    saveReport(p3, {
      date: '2025-05-18', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':    { value: 13.2,   unit: 'g/dL',       normal: [12, 16] },
        'RBC Count':     { value: 4.4,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':     { value: 13600,  unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':{ value: 185000, unit: '/µL',         normal: [150000, 450000] },
        'Lymphocytes':   { value: 18,     unit: '%',           normal: [20, 40] },
        'Neutrophils':   { value: 91,     unit: '%',           normal: [40, 70] },
        'ESR':           { value: 58,     unit: 'mm/hr',       normal: [0, 20] }
      }
    });

    // R4 — 25 Jul 2025 | ADDED | Treatment started — all markers beginning to improve
    saveReport(p3, {
      date: '2025-07-25', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':    { value: 13.8,   unit: 'g/dL',       normal: [12, 16] },
        'RBC Count':     { value: 4.6,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':     { value: 9800,   unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':{ value: 214000, unit: '/µL',         normal: [150000, 450000] },
        'Lymphocytes':   { value: 24,     unit: '%',           normal: [20, 40] },
        'Neutrophils':   { value: 74,     unit: '%',           normal: [40, 70] },
        'ESR':           { value: 34,     unit: 'mm/hr',       normal: [0, 20] }
      }
    });

    // R5 — 22 Oct 2025 | ADDED | Near normal — ESR almost back, neutrophils settling
    saveReport(p3, {
      date: '2025-10-22', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':    { value: 14.6,   unit: 'g/dL',       normal: [12, 16] },
        'RBC Count':     { value: 4.8,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':     { value: 7200,   unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':{ value: 238000, unit: '/µL',         normal: [150000, 450000] },
        'Lymphocytes':   { value: 26,     unit: '%',           normal: [20, 40] },
        'Neutrophils':   { value: 68,     unit: '%',           normal: [40, 70] },
        'ESR':           { value: 22,     unit: 'mm/hr',       normal: [0, 20] }
      }
    });

    // R6 — 15 Jan 2026 | ADDED | Full recovery — all values within normal range
    saveReport(p3, {
      date: '2026-01-15', reportType: 'CBC Blood Test',
      metrics: {
        'Hemoglobin':    { value: 15.1,   unit: 'g/dL',       normal: [12, 16] },
        'RBC Count':     { value: 4.9,    unit: 'million/µL', normal: [4.2, 5.4] },
        'WBC Count':     { value: 6800,   unit: 'cells/µL',   normal: [4000, 11000] },
        'Platelet Count':{ value: 252000, unit: '/µL',         normal: [150000, 450000] },
        'Lymphocytes':   { value: 29,     unit: '%',           normal: [20, 40] },
        'Neutrophils':   { value: 62,     unit: '%',           normal: [40, 70] },
        'ESR':           { value: 14,     unit: 'mm/hr',       normal: [0, 20] }
      }
    });

    // ════════════════════════════════════════════════════════════════════════
    // PATIENT 4 — Ramesh Kumar | Male, 45 | PID: BT30987
    // Story: Early diabetes warning → full-blown uncontrolled diabetes + renal risk
    // Sources: Abnormal_Blood_Test.pdf (R2), R1 ADDED
    // ════════════════════════════════════════════════════════════════════════
    const p4 = addPatient('Ramesh Kumar');

    // R1 — 15 Aug 2025 | ADDED | Early markers — glucose elevated, lipids borderline
    saveReport(p4, {
      date: '2025-08-15', reportType: 'Blood Sugar & Lipid Panel',
      metrics: {
        'Fasting Blood Sugar':      { value: 118,  unit: 'mg/dL', normal: [70, 100] },
        'Postprandial Blood Sugar': { value: 172,  unit: 'mg/dL', normal: [0, 140] },
        'HbA1c':                    { value: 6.4,  unit: '%',     normal: [0, 5.7] },
        'Serum Cholesterol':        { value: 208,  unit: 'mg/dL', normal: [0, 200] },
        'Triglycerides':            { value: 164,  unit: 'mg/dL', normal: [0, 150] },
        'HDL Cholesterol':          { value: 40,   unit: 'mg/dL', normal: [40, 100] },
        'LDL Cholesterol':          { value: 124,  unit: 'mg/dL', normal: [0, 100] },
        'Serum Creatinine':         { value: 1.1,  unit: 'mg/dL', normal: [0.6, 1.3] },
        'Blood Urea':               { value: 32,   unit: 'mg/dL', normal: [15, 40] }
      }
    });

    // R2 — 10 Feb 2026 | Source: Abnormal_Blood_Test.pdf | Poorly controlled T2 Diabetes
    saveReport(p4, {
      date: '2026-02-10', reportType: 'Blood Sugar & Lipid Panel',
      metrics: {
        'Fasting Blood Sugar':      { value: 168,  unit: 'mg/dL', normal: [70, 100] },
        'Postprandial Blood Sugar': { value: 248,  unit: 'mg/dL', normal: [0, 140] },
        'Random Blood Sugar':       { value: 286,  unit: 'mg/dL', normal: [0, 200] },
        'HbA1c':                    { value: 8.6,  unit: '%',     normal: [0, 5.7] },
        'Serum Cholesterol':        { value: 238,  unit: 'mg/dL', normal: [0, 200] },
        'Triglycerides':            { value: 212,  unit: 'mg/dL', normal: [0, 150] },
        'HDL Cholesterol':          { value: 34,   unit: 'mg/dL', normal: [40, 100] },
        'LDL Cholesterol':          { value: 162,  unit: 'mg/dL', normal: [0, 100] },
        'Serum Creatinine':         { value: 1.6,  unit: 'mg/dL', normal: [0.6, 1.3] },
        'Blood Urea':               { value: 52,   unit: 'mg/dL', normal: [15, 40] }
      }
    });
  }

  return {
    getPatients,
    addPatient,
    getPatientById,
    getReports,
    saveReport,
    deleteReport,
    getMetricTimelines,
    seedDemoData
  };
})();
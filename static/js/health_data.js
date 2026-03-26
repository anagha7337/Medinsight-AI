/**
 * health_data.js  —  Supabase-backed health data layer
 *
 * Replaces the old localStorage version.
 * All functions are async and return data from Supabase.
 *
 * Exposed as window.HealthData so trend_tracking.html can call it the same way.
 */

const HealthData = (() => {

    // ── Supabase client (credentials injected by Flask via Jinja2) ──────────
    // trend_tracking.html must include the Supabase CDN script AND expose
    // SUPABASE_URL / SUPABASE_ANON_KEY as globals before loading this file.
    let _supabase = null;

    function init(url, key) {
        const { createClient } = supabase;   // from CDN
        _supabase = createClient(url, key);
    }

    // ── Patients ────────────────────────────────────────────────────────────

    async function getPatients(userId) {
        const { data, error } = await _supabase
            .from('patients')
            .select('id, name, created_at')
            .eq('owner_id', userId)
            .order('created_at', { ascending: true });
        if (error) { console.error('getPatients:', error); return []; }
        return data || [];
    }

    async function addPatient(userId, name) {
        const { data, error } = await _supabase
            .from('patients')
            .insert({ owner_id: userId, name })
            .select()
            .single();
        if (error) { console.error('addPatient:', error); return null; }
        return data;          // { id, name, … }
    }

    // ── Reports ─────────────────────────────────────────────────────────────

    /**
     * Returns all reports for a patient, sorted by date ascending.
     * Each row: { id, report_date, report_type, metrics: { TestName: { value, unit, normal, status } } }
     */
    async function getReports(patientId, userId) {
        const { data, error } = await _supabase
            .from('health_reports')
            .select('id, report_date, report_type, metrics, created_at')
            .eq('patient_id', patientId)
            .eq('owner_id', userId)
            .order('report_date', { ascending: true });
        if (error) { console.error('getReports:', error); return []; }
        return data || [];
    }

    async function deleteReport(reportId, userId) {
        const { error } = await _supabase
            .from('health_reports')
            .delete()
            .eq('id', reportId)
            .eq('owner_id', userId);
        if (error) { console.error('deleteReport:', error); }
    }

    // ── Metric timelines ────────────────────────────────────────────────────

    /**
     * Returns { MetricName: [ { date, value, unit, normal, status } ] }
     * sorted chronologically per metric — ready for Chart.js.
     */
    function buildMetricTimelines(reports) {
        const timelines = {};
        reports.forEach(report => {
            if (!report.metrics) return;
            Object.entries(report.metrics).forEach(([metric, info]) => {
                if (!timelines[metric]) timelines[metric] = [];
                timelines[metric].push({
                    date:       report.report_date,
                    value:      info.value,
                    unit:       info.unit       || '',
                    normal:     info.normal     || null,   // [min, max] or null
                    status:     info.status     || 'normal',
                    reportId:   report.id,
                    reportType: report.report_type
                });
            });
        });
        // Each list is already sorted because getReports() orders by date
        return timelines;
    }

    // ── Public API ──────────────────────────────────────────────────────────
    return { init, getPatients, addPatient, getReports, deleteReport, buildMetricTimelines };

})();
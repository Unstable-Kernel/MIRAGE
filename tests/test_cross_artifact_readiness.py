from mirage.runtime import (
    ApprovalChainAssessment,
    ApprovalChainStatus,
    ContextBundleStatus,
    ControlledContextAssessment,
    CrossArtifactStatus,
    DeterministicReportAssessment,
    DeterministicReportSection,
    DeterministicReportStatus,
    DeterministicReviewPolicy,
    DeterministicReviewReport,
    DispatchEligibilityAssessment,
    DispatchEligibilityStatus,
    ReportProvenanceAssessment,
    ReportProvenanceStatus,
    ReviewPolicyStatus,
    ReviewTraceAssessment,
    assess_cross_artifacts,
    assess_review_policy,
    assess_workflow_readiness,
)


def test_consistent_review_artifacts_remain_blocked_on_external_prerequisites():
    context = ControlledContextAssessment(envelope_id="envelope-v1", workflow_id="workflow-v1", status="ready_for_review", claim_ids={"claim-v1"})
    trace = ReviewTraceAssessment(trace_id="trace-v1", workflow_id="workflow-v1", status="ready_for_review")
    approval = ApprovalChainAssessment(chain_id="chain-v1", workflow_id="workflow-v1", trace_id="trace-v1", status=ApprovalChainStatus.REVIEW_READY)
    report = DeterministicReviewReport(
        report_id="report-v1",
        workflow_id="workflow-v1",
        context_envelope_id="envelope-v1",
        sections=[DeterministicReportSection(section_id="summary", title="Review inputs", context_claim_ids={"claim-v1"})],
    )
    report_assessment = DeterministicReportAssessment(report_id="report-v1", workflow_id="workflow-v1", status=DeterministicReportStatus.READY_FOR_REVIEW)
    provenance = ReportProvenanceAssessment(report_id="report-v1", status=ReportProvenanceStatus.READY_FOR_REVIEW)
    cross = assess_cross_artifacts(context, trace, approval, report_assessment, provenance)
    policy = assess_review_policy(DeterministicReviewPolicy(policy_id="review-policy-v1"), report, cross)
    dispatch = DispatchEligibilityAssessment(
        workflow_id="workflow-v1",
        status=DispatchEligibilityStatus.INELIGIBLE,
        reasons=["verified live read-only transport is unavailable", "enforced sandbox evidence is unavailable"],
    )

    readiness = assess_workflow_readiness(cross, policy, dispatch)

    assert context.status == ContextBundleStatus.READY_FOR_REVIEW
    assert cross.status == CrossArtifactStatus.CONSISTENT
    assert policy.status == ReviewPolicyStatus.READY_FOR_REVIEW
    assert readiness.status.value == "ready_for_external_prerequisites"
    assert readiness.execution_permitted is False
    assert readiness.denial_reasons == dispatch.reasons

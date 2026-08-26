import Foundation

@MainActor
final class RuleReviewViewModel: ObservableObject {
    @Published private(set) var rules: [ReviewRule] = []
    @Published private(set) var chapters: [ChapterSummary] = []
    @Published private(set) var summary: ReviewSummary = .empty
    @Published private(set) var totalRules: Int = 0
    @Published private(set) var isLoading = false
    @Published private(set) var savingRuleID: String?
    @Published var errorMessage: String?
    @Published var selectedRuleID: String?
    @Published var searchText = ""
    @Published var selectedChapter: Int?
    @Published var decisionFilter: ReviewDecision?
    @Published var classificationFilter = "all"
    @Published var statusFilter = "all"
    @Published var reviewerName: String {
        didSet {
            UserDefaults.standard.set(reviewerName, forKey: Self.reviewerNameKey)
        }
    }

    private static let reviewerNameKey = "KingsAstrologyReviewerName"
    private let api: APIClient

    init(api: APIClient = APIClient()) {
        self.api = api
        self.reviewerName = UserDefaults.standard.string(forKey: Self.reviewerNameKey) ?? ""
    }

    var filteredRules: [ReviewRule] {
        let query = searchText.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()

        return rules.filter { rule in
            if let selectedChapter, rule.chapter != selectedChapter {
                return false
            }

            if let decisionFilter, rule.review.decision != decisionFilter {
                return false
            }

            if classificationFilter != "all", rule.classification != classificationFilter {
                return false
            }

            if statusFilter != "all", rule.status != statusFilter {
                return false
            }

            if !query.isEmpty, !rule.searchableText.contains(query) {
                return false
            }

            return true
        }
    }

    var selectedRule: ReviewRule? {
        guard let selectedRuleID else {
            return filteredRules.first ?? rules.first
        }

        return rules.first { $0.id == selectedRuleID } ?? filteredRules.first ?? rules.first
    }

    var classifications: [String] {
        Array(Set(rules.map(\.classification))).sorted()
    }

    var statuses: [String] {
        Array(Set(rules.map(\.status))).sorted()
    }

    var completionFraction: Double {
        guard summary.total > 0 else {
            return 0
        }

        return Double(summary.approved + summary.needsImprovement) / Double(summary.total)
    }

    func load() async {
        isLoading = true
        errorMessage = nil

        do {
            let envelope = try await api.fetchRules()
            rules = envelope.rules
            chapters = envelope.chapters
            summary = envelope.summary
            totalRules = envelope.totalRules

            if selectedRuleID == nil || selectedRule == nil {
                selectedRuleID = filteredRules.first?.id ?? rules.first?.id
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func select(_ rule: ReviewRule) {
        selectedRuleID = rule.id
    }

    func resetFilters() {
        searchText = ""
        selectedChapter = nil
        decisionFilter = nil
        classificationFilter = "all"
        statusFilter = "all"
    }

    func saveReview(
        for rule: ReviewRule,
        decision: ReviewDecision,
        comments: String,
        improvements: String,
        reviewer: String
    ) async {
        savingRuleID = rule.id
        errorMessage = nil

        let draft = ReviewDraft(
            decision: decision,
            comments: comments,
            improvements: improvements,
            reviewer: reviewer
        )

        do {
            let response = try await api.saveReview(ruleID: rule.id, draft: draft)
            if let index = rules.firstIndex(where: { $0.id == rule.id }) {
                rules[index].review = response.review
            }
            summary = response.summary
            reviewerName = reviewer
        } catch {
            errorMessage = error.localizedDescription
        }

        savingRuleID = nil
    }
}

import Foundation
import SwiftUI

enum ReviewDecision: String, Codable, CaseIterable, Identifiable {
    case unreviewed
    case approved
    case needsImprovement = "needs_improvement"

    var id: String { rawValue }

    var label: String {
        switch self {
        case .unreviewed:
            "Unreviewed"
        case .approved:
            "Approved"
        case .needsImprovement:
            "Needs work"
        }
    }

    var systemImage: String {
        switch self {
        case .unreviewed:
            "circle.dashed"
        case .approved:
            "checkmark.seal.fill"
        case .needsImprovement:
            "exclamationmark.triangle.fill"
        }
    }

    var tint: Color {
        switch self {
        case .unreviewed:
            .secondary
        case .approved:
            .green
        case .needsImprovement:
            .orange
        }
    }
}

struct ReviewSummary: Codable, Equatable {
    var approved: Int
    var needsImprovement: Int
    var unreviewed: Int

    enum CodingKeys: String, CodingKey {
        case approved
        case needsImprovement = "needs_improvement"
        case unreviewed
    }

    static let empty = ReviewSummary(approved: 0, needsImprovement: 0, unreviewed: 0)

    var total: Int {
        approved + needsImprovement + unreviewed
    }
}

struct ChapterSummary: Decodable, Hashable, Identifiable {
    var id: Int { chapter }

    let chapter: Int
    let title: String
    let sourceFile: String
    let ruleCount: Int
    let warnings: [String]

    enum CodingKeys: String, CodingKey {
        case chapter
        case title
        case sourceFile = "source_file"
        case ruleCount = "rule_count"
        case warnings
    }
}

struct RuleCitation: Decodable, Hashable, Identifiable {
    var id: String { raw }

    let raw: String
    let chapter: Int?
    let verse: String?
}

struct RuleReview: Codable, Hashable {
    var ruleID: String
    var decision: ReviewDecision
    var comments: String
    var improvements: String
    var reviewer: String
    var updatedAt: String

    enum CodingKeys: String, CodingKey {
        case ruleID = "rule_id"
        case decision
        case comments
        case improvements
        case reviewer
        case updatedAt = "updated_at"
    }

    static func blank(ruleID: String) -> RuleReview {
        RuleReview(
            ruleID: ruleID,
            decision: .unreviewed,
            comments: "",
            improvements: "",
            reviewer: "",
            updatedAt: ""
        )
    }

    var updatedDisplay: String {
        guard !updatedAt.isEmpty else {
            return "Not saved yet"
        }

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]

        if let date = formatter.date(from: updatedAt) {
            return date.formatted(date: .abbreviated, time: .shortened)
        }

        formatter.formatOptions = [.withInternetDateTime]
        if let date = formatter.date(from: updatedAt) {
            return date.formatted(date: .abbreviated, time: .shortened)
        }

        return updatedAt
    }
}

struct ReviewRule: Decodable, Hashable, Identifiable {
    let id: String
    let rawID: String
    let title: String
    let chapter: Int
    let sourceFile: String
    let classification: String
    let status: String
    let citations: [RuleCitation]
    let condition: String
    let effect: String
    let verseSource: String
    let notes: String
    let warnings: [String]
    var review: RuleReview

    enum CodingKeys: String, CodingKey {
        case id
        case rawID = "raw_id"
        case title
        case chapter
        case sourceFile = "source_file"
        case classification
        case status
        case citations
        case condition
        case effect
        case verseSource = "verse_source"
        case notes
        case warnings
        case review
    }

    var searchableText: String {
        [
            id,
            rawID,
            title,
            "Chapter \(chapter)",
            classification,
            status,
            condition,
            effect,
            verseSource,
            notes,
            citations.map(\.raw).joined(separator: " ")
        ].joined(separator: " ").lowercased()
    }
}

struct RulesEnvelope: Decodable {
    let rules: [ReviewRule]
    let totalRules: Int
    let filteredRules: Int
    let summary: ReviewSummary
    let chapters: [ChapterSummary]

    enum CodingKeys: String, CodingKey {
        case rules
        case totalRules = "total_rules"
        case filteredRules = "filtered_rules"
        case summary
        case chapters
    }
}

struct ReviewDraft: Encodable {
    var decision: ReviewDecision
    var comments: String
    var improvements: String
    var reviewer: String
}

struct SaveReviewResponse: Decodable {
    let review: RuleReview
    let summary: ReviewSummary
}

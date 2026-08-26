import SwiftUI

struct RuleReviewScreen: View {
    @StateObject private var model = RuleReviewViewModel()

    var body: some View {
        NavigationSplitView {
            RuleSidebar(model: model)
                .navigationTitle("Rule Review")
        } detail: {
            if let rule = model.selectedRule {
                RuleDetailView(rule: rule, model: model)
                    .id(rule.id)
            } else {
                EmptyRulesView()
            }
        }
        .task {
            if model.rules.isEmpty {
                await model.load()
            }
        }
        .alert("Backend Error", isPresented: Binding(
            get: { model.errorMessage != nil },
            set: { if !$0 { model.errorMessage = nil } }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(model.errorMessage ?? "")
        }
    }
}

private struct RuleSidebar: View {
    @ObservedObject var model: RuleReviewViewModel

    var body: some View {
        VStack(spacing: 0) {
            DashboardHeader(model: model)
                .padding(.horizontal, 16)
                .padding(.top, 14)
                .padding(.bottom, 10)

            FilterPanel(model: model)
                .padding(.horizontal, 16)
                .padding(.bottom, 10)

            Divider()

            if model.isLoading && model.rules.isEmpty {
                ProgressView("Loading rules")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if model.filteredRules.isEmpty {
                EmptyFilterView(reset: model.resetFilters)
            } else {
                List(selection: $model.selectedRuleID) {
                    ForEach(model.filteredRules) { rule in
                        NavigationLink(value: rule.id) {
                            RuleRow(rule: rule, isSelected: model.selectedRuleID == rule.id)
                        }
                        .tag(rule.id)
                        .listRowInsets(EdgeInsets(top: 8, leading: 12, bottom: 8, trailing: 12))
                        .listRowBackground(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(model.selectedRuleID == rule.id ? Color.accentColor.opacity(0.13) : Color.clear)
                                .padding(.horizontal, 6)
                                .padding(.vertical, 2)
                        )
                    }
                }
                .listStyle(.plain)
                .refreshable {
                    await model.load()
                }
            }
        }
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    Task { await model.load() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .disabled(model.isLoading)
                .accessibilityLabel("Refresh")
            }
        }
    }
}

private struct DashboardHeader: View {
    @ObservedObject var model: RuleReviewViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Brihat Jataka")
                        .font(.headline)
                    Text("Chapters 8-20")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                Spacer()

                Text("\(model.summary.approved + model.summary.needsImprovement)/\(max(model.summary.total, model.totalRules))")
                    .font(.system(.title3, design: .rounded, weight: .semibold))
                    .monospacedDigit()
            }

            ProgressView(value: model.completionFraction)
                .tint(.green)

            HStack(spacing: 8) {
                SummaryBadge(title: "Approved", value: model.summary.approved, color: .green, image: "checkmark.seal.fill")
                SummaryBadge(title: "Needs work", value: model.summary.needsImprovement, color: .orange, image: "exclamationmark.triangle.fill")
                SummaryBadge(title: "Open", value: model.summary.unreviewed, color: .secondary, image: "circle.dashed")
            }
        }
    }
}

private struct SummaryBadge: View {
    let title: String
    let value: Int
    let color: Color
    let image: String

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Image(systemName: image)
                .font(.caption.weight(.semibold))
                .foregroundStyle(color)
            Text("\(value)")
                .font(.system(.headline, design: .rounded, weight: .semibold))
                .monospacedDigit()
            Text(title)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
        .frame(maxWidth: .infinity, minHeight: 74, alignment: .leading)
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 8))
    }
}

private struct FilterPanel: View {
    @ObservedObject var model: RuleReviewViewModel

    var body: some View {
        VStack(spacing: 10) {
            HStack(spacing: 8) {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(.secondary)
                TextField("Search rule text", text: $model.searchText)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
            }
            .padding(10)
            .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 8))

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    FilterChip(
                        title: "All chapters",
                        isSelected: model.selectedChapter == nil,
                        action: { model.selectedChapter = nil }
                    )

                    ForEach(model.chapters) { chapter in
                        FilterChip(
                            title: "Ch \(chapter.chapter)",
                            isSelected: model.selectedChapter == chapter.chapter,
                            action: { model.selectedChapter = chapter.chapter }
                        )
                    }
                }
            }

            HStack(spacing: 8) {
                Menu {
                    Button("All decisions") { model.decisionFilter = nil }
                    ForEach(ReviewDecision.allCases) { decision in
                        Button(decision.label) { model.decisionFilter = decision }
                    }
                } label: {
                    MenuChip(
                        title: model.decisionFilter?.label ?? "Decision",
                        image: model.decisionFilter?.systemImage ?? "line.3.horizontal.decrease.circle"
                    )
                }

                Menu {
                    Button("All classes") { model.classificationFilter = "all" }
                    ForEach(model.classifications, id: \.self) { classification in
                        Button(classification.capitalized) { model.classificationFilter = classification }
                    }
                } label: {
                    MenuChip(title: model.classificationFilter == "all" ? "Class" : model.classificationFilter.capitalized, image: "tag")
                }

                Menu {
                    Button("All status") { model.statusFilter = "all" }
                    ForEach(model.statuses, id: \.self) { status in
                        Button(status.capitalized) { model.statusFilter = status }
                    }
                } label: {
                    MenuChip(title: model.statusFilter == "all" ? "Status" : model.statusFilter.capitalized, image: "doc.text.magnifyingglass")
                }
            }
        }
    }
}

private struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline.weight(.medium))
                .lineLimit(1)
                .padding(.horizontal, 11)
                .padding(.vertical, 7)
                .background(isSelected ? Color.accentColor : Color(uiColor: .secondarySystemGroupedBackground), in: Capsule())
                .foregroundStyle(isSelected ? .white : .primary)
        }
        .buttonStyle(.plain)
    }
}

private struct MenuChip: View {
    let title: String
    let image: String

    var body: some View {
        Label(title, systemImage: image)
            .font(.subheadline.weight(.medium))
            .lineLimit(1)
            .minimumScaleFactor(0.75)
            .frame(maxWidth: .infinity)
            .padding(.horizontal, 10)
            .padding(.vertical, 8)
            .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 8))
            .foregroundStyle(.primary)
    }
}

private struct RuleRow: View {
    let rule: ReviewRule
    let isSelected: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Text(rule.id)
                    .font(.caption.weight(.semibold))
                    .monospaced()
                    .foregroundStyle(.secondary)

                Spacer(minLength: 4)

                DecisionPill(decision: rule.review.decision)
            }

            Text(rule.title)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.primary)
                .lineLimit(2)

            Text(rule.condition)
                .font(.caption)
                .foregroundStyle(.secondary)
                .lineLimit(3)

            HStack(spacing: 6) {
                Text("Ch \(rule.chapter)")
                Text(rule.classification.capitalized)
                Text(rule.status.capitalized)
            }
            .font(.caption2.weight(.medium))
            .foregroundStyle(isSelected ? Color.accentColor : .secondary)
        }
        .padding(.vertical, 6)
    }
}

private struct RuleDetailView: View {
    let rule: ReviewRule
    @ObservedObject var model: RuleReviewViewModel
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                RuleDetailHeader(rule: rule)

                if horizontalSizeClass == .compact {
                    VStack(alignment: .leading, spacing: 14) {
                        ConditionPanel(rule: rule)
                        EffectPanel(rule: rule)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                } else {
                    HStack(alignment: .top, spacing: 14) {
                        ConditionPanel(rule: rule)
                        EffectPanel(rule: rule)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }

                DetailPanel(title: "Verse Source", image: "quote.bubble") {
                    Text(rule.verseSource.isEmpty ? "No verse text captured." : rule.verseSource)
                        .textSelection(.enabled)
                }

                if !rule.notes.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    DetailPanel(title: "Notes", image: "note.text") {
                        Text(rule.notes)
                    }
                }

                if !rule.warnings.isEmpty {
                    DetailPanel(title: "Warnings", image: "exclamationmark.triangle") {
                        VStack(alignment: .leading, spacing: 8) {
                            ForEach(rule.warnings, id: \.self) { warning in
                                Label(warning, systemImage: "exclamationmark.circle")
                                    .foregroundStyle(.orange)
                            }
                        }
                    }
                }

                ReviewEditor(rule: rule, model: model)
            }
            .font(.body)
            .lineSpacing(2)
            .padding(20)
            .frame(maxWidth: 980, alignment: .leading)
        }
        .background(Color(uiColor: .systemGroupedBackground))
        .navigationTitle(rule.id)
        .navigationBarTitleDisplayMode(.inline)
    }
}

private struct RuleDetailHeader: View {
    let rule: ReviewRule
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 12) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Chapter \(rule.chapter)")
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(Color.accentColor)

                    Text(rule.title)
                        .font((horizontalSizeClass == .compact ? Font.title3 : Font.title2).weight(.semibold))
                        .fixedSize(horizontal: false, vertical: true)
                }

                Spacer()

                DecisionPill(decision: rule.review.decision)
            }

            HStack(spacing: 8) {
                Label(rule.classification.capitalized, systemImage: "tag")
                Label(rule.status.capitalized, systemImage: "doc.text")
                Label(rule.review.updatedDisplay, systemImage: "clock")
            }
            .font(.caption)
            .foregroundStyle(.secondary)

            if !rule.citations.isEmpty {
                FlowLayout(items: rule.citations) { citation in
                    Text(citation.raw)
                        .font(.caption.weight(.semibold))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color.accentColor.opacity(0.12), in: Capsule())
                        .foregroundStyle(Color.accentColor)
                }
            }
        }
        .padding(18)
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 8))
    }
}

private struct ConditionPanel: View {
    let rule: ReviewRule

    var body: some View {
        DetailPanel(title: "Condition", image: "scope") {
            Text(rule.condition)
        }
    }
}

private struct EffectPanel: View {
    let rule: ReviewRule

    var body: some View {
        DetailPanel(title: "Effect", image: "sparkles") {
            Text(rule.effect)
        }
    }
}

private struct DetailPanel<Content: View>: View {
    let title: String
    let image: String
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: image)
                .font(.headline)
                .foregroundStyle(.primary)

            content
                .foregroundStyle(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .topLeading)
        .background(Color(uiColor: .secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 8))
    }
}

private struct ReviewEditor: View {
    let rule: ReviewRule
    @ObservedObject var model: RuleReviewViewModel
    @State private var decision: ReviewDecision
    @State private var comments: String
    @State private var improvements: String
    @State private var reviewer: String

    init(rule: ReviewRule, model: RuleReviewViewModel) {
        self.rule = rule
        self.model = model
        _decision = State(initialValue: rule.review.decision)
        _comments = State(initialValue: rule.review.comments)
        _improvements = State(initialValue: rule.review.improvements)
        _reviewer = State(initialValue: rule.review.reviewer.isEmpty ? model.reviewerName : rule.review.reviewer)
    }

    var body: some View {
        DetailPanel(title: "Review", image: "square.and.pencil") {
            VStack(alignment: .leading, spacing: 14) {
                Picker("Decision", selection: $decision) {
                    ForEach(ReviewDecision.allCases) { decision in
                        Label(decision.label, systemImage: decision.systemImage)
                            .tag(decision)
                    }
                }
                .pickerStyle(.segmented)

                TextField("Reviewer", text: $reviewer)
                    .textContentType(.name)
                    .textFieldStyle(.roundedBorder)

                VStack(alignment: .leading, spacing: 8) {
                    Text("Comments")
                        .font(.subheadline.weight(.semibold))
                    TextEditor(text: $comments)
                        .frame(minHeight: 110)
                        .scrollContentBackground(.hidden)
                        .padding(8)
                        .background(Color(uiColor: .systemBackground), in: RoundedRectangle(cornerRadius: 8))
                }

                VStack(alignment: .leading, spacing: 8) {
                    Text("Improvements")
                        .font(.subheadline.weight(.semibold))
                    TextEditor(text: $improvements)
                        .frame(minHeight: 110)
                        .scrollContentBackground(.hidden)
                        .padding(8)
                        .background(Color(uiColor: .systemBackground), in: RoundedRectangle(cornerRadius: 8))
                }

                HStack {
                    Label(rule.review.updatedDisplay, systemImage: "clock")
                        .font(.caption)
                        .foregroundStyle(.secondary)

                    Spacer()

                    Button {
                        Task {
                            await model.saveReview(
                                for: rule,
                                decision: decision,
                                comments: comments,
                                improvements: improvements,
                                reviewer: reviewer
                            )
                        }
                    } label: {
                        Label(model.savingRuleID == rule.id ? "Saving" : "Save Review", systemImage: "tray.and.arrow.down")
                            .frame(minWidth: 136)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(model.savingRuleID == rule.id)
                }
            }
        }
    }
}

private struct DecisionPill: View {
    let decision: ReviewDecision

    var body: some View {
        Label(decision.label, systemImage: decision.systemImage)
            .font(.caption.weight(.semibold))
            .lineLimit(1)
            .minimumScaleFactor(0.75)
            .padding(.horizontal, 9)
            .padding(.vertical, 5)
            .background(decision.tint.opacity(0.14), in: Capsule())
            .foregroundStyle(decision.tint)
    }
}

private struct EmptyRulesView: View {
    var body: some View {
        ContentUnavailableView(
            "No Rule Selected",
            systemImage: "doc.text.magnifyingglass",
            description: Text("Select a rule to review its source, citations, comments, and approval status.")
        )
    }
}

private struct EmptyFilterView: View {
    let reset: () -> Void

    var body: some View {
        ContentUnavailableView {
            Label("No matching rules", systemImage: "line.3.horizontal.decrease.circle")
        } description: {
            Text("Adjust the current filters to continue reviewing.")
        } actions: {
            Button("Reset Filters", action: reset)
                .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

private struct FlowLayout<Item: Identifiable, Content: View>: View {
    let items: [Item]
    let content: (Item) -> Content

    var body: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 92), spacing: 8)], alignment: .leading, spacing: 8) {
            ForEach(items) { item in
                content(item)
            }
        }
    }
}

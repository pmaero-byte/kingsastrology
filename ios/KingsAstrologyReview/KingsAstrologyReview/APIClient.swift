import Foundation

enum APIClientError: LocalizedError {
    case invalidURL
    case badStatus(Int, String)
    case decoding(Error)
    case transport(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            "The backend URL is invalid."
        case .badStatus(let status, let message):
            "The backend returned HTTP \(status). \(message)"
        case .decoding(let error):
            "The backend response could not be read. \(error.localizedDescription)"
        case .transport(let error):
            "Could not reach the backend. \(error.localizedDescription)"
        }
    }
}

final class APIClient {
    private let baseURL: URL
    private let session: URLSession
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    init(
        baseURL: URL = URL(string: "http://127.0.0.1:8000")!,
        session: URLSession = .shared
    ) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = JSONDecoder()
        self.encoder = JSONEncoder()
    }

    func fetchRules() async throws -> RulesEnvelope {
        let url = baseURL.appendingPathComponent("review/api/rules")
        let request = URLRequest(url: url)
        return try await execute(request, as: RulesEnvelope.self)
    }

    func saveReview(ruleID: String, draft: ReviewDraft) async throws -> SaveReviewResponse {
        guard let encodedRuleID = ruleID.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) else {
            throw APIClientError.invalidURL
        }

        let url = baseURL
            .appendingPathComponent("review/api/rules")
            .appendingPathComponent(encodedRuleID)
            .appendingPathComponent("review")

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encoder.encode(draft)
        return try await execute(request, as: SaveReviewResponse.self)
    }

    private func execute<T: Decodable>(_ request: URLRequest, as type: T.Type) async throws -> T {
        do {
            let (data, response) = try await session.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIClientError.badStatus(-1, "Missing HTTP response.")
            }

            guard (200..<300).contains(httpResponse.statusCode) else {
                let message = String(data: data, encoding: .utf8) ?? ""
                throw APIClientError.badStatus(httpResponse.statusCode, message)
            }

            do {
                return try decoder.decode(type, from: data)
            } catch {
                throw APIClientError.decoding(error)
            }
        } catch let error as APIClientError {
            throw error
        } catch {
            throw APIClientError.transport(error)
        }
    }
}

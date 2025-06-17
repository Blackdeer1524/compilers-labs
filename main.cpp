#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <optional>
#include <stack>
#include <string>
#include <string_view>
#include <tuple>
#include <unordered_map>
#include <vector>

using std::cout;
using std::optional;
using std::string;
using std::vector;

constexpr static uint64_t LAMBDA_INDEX = 0;

// двумерная таблица [состояние][симол] -> список состояний
using nondet_transitions = vector<vector<vector<uint64_t>>>;

class DFSTraverser {
 public:
    explicit DFSTraverser(const nondet_transitions &delta)
        : delta_(delta), visited_(delta.size()) {
    }

    // Достижимые вершины (включая start)
    // (λ не "съедает" символ)
    auto closure(const uint64_t start) -> vector<uint64_t> {
        visited_.assign(visited_.size(), false);
        reachable_.clear();

        fill_reachable(start);
        std::sort(reachable_.begin(), reachable_.end());
        return reachable_;
    }

    auto closure(const vector<uint64_t> &start) -> vector<uint64_t> {
        visited_.assign(visited_.size(), false);
        reachable_.clear();

        for (const uint64_t state : start) {
            if (!visited_.at(state)) {
                fill_reachable(state);
            }
        }

        std::sort(reachable_.begin(), reachable_.end());
        return reachable_;
    }

 private:
    const nondet_transitions &delta_;
    vector<uint64_t> reachable_;
    vector<bool> visited_;

    auto fill_reachable(uint64_t start) -> void {
        visited_.at(start) = true;
        reachable_.push_back(start);

        const auto &next_candidates = delta_.at(start).at(LAMBDA_INDEX);
        for (const uint64_t next_state : next_candidates) {
            if (visited_.at(next_state)) {
                continue;
            }
            fill_reachable(next_state);
        }
    }
};

auto vect2string(const vector<uint64_t> &states, const string &sep = " ")
    -> string {
    if (states.empty()) {
        return "";
    }

    string res;
    for (uint64_t i = 0; i < states.size() - 1; ++i) {
        res += std::to_string(states.at(i)) + sep;
    }
    res += std::to_string(states.at(states.size() - 1));
    return res;
}

auto vect2string(const vector<string> &states, const string &sep = " ")
    -> string {
    if (states.empty()) {
        return "";
    }

    string res;
    for (uint64_t i = 0; i < states.size() - 1; ++i) {
        res += states.at(i) + sep;
    }
    res += states.at(states.size() - 1);
    return res;
}

struct DetAutomaton {
    using StateIndex = uint64_t;

    vector<vector<std::optional<StateIndex>>> delta;
    vector<bool> is_final;
    vector<string> state_index_to_labels;
};

auto det(const nondet_transitions &delta, const vector<bool> &final, uint64_t q)
    -> std::tuple<vector<vector<std::optional<uint64_t>>>,
                  vector<bool>,
                  vector<string>> {
    DFSTraverser traverser(delta);
    const vector<uint64_t> q0 = traverser.closure(q);

    vector<vector<std::optional<uint64_t>>> det_delta;
    vector<bool> det_is_final;

    std::stack<std::tuple<vector<uint64_t>, uint64_t>> s;
    const auto q0_label = vect2string(q0);
    s.emplace(q0, 0);
    std::unordered_map<string, uint64_t> state_label2index{
        {q0_label, 0}
    };
    uint64_t det_states_count = 1;

    while (!s.empty()) {
        const auto [reachable_states, det_state_index] = s.top();
        det_is_final.resize(std::max(det_is_final.size(), det_state_index + 1));
        s.pop();

        for (const uint64_t reachable_state : reachable_states) {
            if (final.at(reachable_state)) {
                det_is_final.at(det_state_index) = true;
                break;
            }
        }

        for (uint64_t in_symbol_i = LAMBDA_INDEX + 1;
             in_symbol_i < delta.at(0).size();
             ++in_symbol_i) {
            vector<uint64_t> next_states_candidates;
            for (const uint64_t reachable_state : reachable_states) {
                const auto &neighbours =
                    delta.at(reachable_state).at(in_symbol_i);
                std::copy(neighbours.begin(),
                          neighbours.end(),
                          std::back_inserter(next_states_candidates));
            }
            vector<uint64_t> next_states =
                traverser.closure(next_states_candidates);

            const auto next_state_label = vect2string(next_states);
            uint64_t next_state_index;
            if (const auto found = state_label2index.find(next_state_label);
                found == state_label2index.end()) {
                next_state_index = det_states_count;
                ++det_states_count;
                state_label2index.insert({next_state_label, next_state_index});
                s.emplace(next_states, next_state_index);
            } else {
                next_state_index = found->second;
            }

            det_delta.resize(std::max(det_delta.size(), det_state_index + 1));
            det_delta.at(det_state_index)
                .resize(std::max(det_delta.at(det_state_index).size(),
                                 in_symbol_i + 1));

            det_delta.at(det_state_index).at(in_symbol_i) = next_state_index;
        }
    }

    vector<string> index2state_label;
    index2state_label.resize(state_label2index.size());
    for (const auto &[key, index] : state_label2index) {
        index2state_label.at(index) = (key);
    }

    return {det_delta, det_is_final, index2state_label};
}

auto print_automaton(const vector<string> &alphabet,
                     const vector<vector<std::optional<uint64_t>>> &delta,
                     const vector<bool> &final,
                     const vector<string> &index2name) -> void {
    std::cout << "digraph {" << std::endl;
    std::cout << "    rankdir = LR" << std::endl;
    for (uint64_t state_i = 0; state_i < index2name.size(); ++state_i) {
        const auto &state_label = index2name.at(state_i);
        std::cout << "    " << std::to_string(state_i)
                  << " [label = \"[" + state_label + "]\", shape = ";
        if (final.at(state_i)) {
            std::cout << "doublecircle]" << std::endl;
        } else {
            std::cout << "circle]" << std::endl;
        }
    }
    for (uint64_t cur_state_i = 0; cur_state_i < delta.size(); ++cur_state_i) {
        std::unordered_map<uint64_t, vector<string>> arrows;
        for (uint64_t in_symbol_i = 0; in_symbol_i < delta.at(0).size();
             ++in_symbol_i) {
            const auto next_state_opt = delta.at(cur_state_i).at(in_symbol_i);
            if (!next_state_opt.has_value()) {
                continue;
            }
            const auto next_state_i = next_state_opt.value();
            const auto &in_symbol = alphabet.at(in_symbol_i);
            arrows[next_state_i].push_back(in_symbol);
        }
        for (const auto &[next_state_i, in_symbols] : arrows) {
            std::cout << "    " << cur_state_i << " -> " << next_state_i
                      << " [label = \"" + vect2string(in_symbols, ", ") + "\"]"
                      << std::endl;
        }
    }
    std::cout << "}" << std::endl;
}

auto pad_mid(std::string_view s, size_t l) -> string {
    string res;
    res.resize((std::max(s.size(), l)));

    const size_t left_pad = (res.size() - s.size()) / 2;
    const size_t right_pad = res.size() - s.size() - left_pad;

    std::fill(res.begin(), res.begin() + left_pad, ' ');
    std::copy(s.begin(), s.end(), res.begin() + left_pad);
    std::fill(res.end() - right_pad, res.end(), ' ');
    return res;
}

void print_table(const vector<string> &alphabet,
                 const vector<vector<optional<uint64_t>>> &det_delta,
                 const vector<string> &state_index2label) {
    const size_t pad = 11;

    cout << "Table: " << '\n';
    cout << " | " << pad_mid("", pad) << " | ";
    for (size_t i = LAMBDA_INDEX + 1; i < alphabet.size(); ++i) {
        const auto &a = alphabet.at(i);
        cout << pad_mid(a, pad) << " | ";
    }
    cout << '\n';

    for (int i = 0; i < det_delta.size(); ++i) {
        const vector<optional<uint64_t>> &row = det_delta.at(i);
        cout << " | " << pad_mid(state_index2label.at(i), pad) << " | ";
        for (size_t symbol_i = LAMBDA_INDEX + 1; symbol_i < row.size();
             ++symbol_i) {
            const optional<uint64_t> next_state_i = row.at(symbol_i);
            if (next_state_i.has_value()) {
                const auto &l = state_index2label.at(next_state_i.value());
                if (!l.empty()) {
                    cout << pad_mid(l, pad) << " | ";
                } else {
                    cout << pad_mid("TRAP", pad) << " | ";
                }
            } else {
                cout << pad_mid("-", pad) << " | ";
            }
        }
        cout << '\n';
    }
    cout << '\n';
}

auto main() -> int {
    uint64_t states_count;
    uint64_t transitions_count;
    std::cin >> states_count >> transitions_count;

    vector<vector<vector<uint64_t>>> delta(states_count,
                                           vector<vector<uint64_t>>(1));
    std::unordered_map<string, uint64_t> symbol2index{
        {"lambda", LAMBDA_INDEX},
    };
    uint64_t alphabet_size = 1;  // 0 уже заняли лямбдой

    for (uint64_t i = 0; i < transitions_count; ++i) {
        uint64_t from;
        uint64_t to;
        string transition_signal;
        std::cin >> from >> to >> transition_signal;
        uint64_t transition_signal_index;
        if (const auto found = symbol2index.find(transition_signal);
            found == symbol2index.end()) {
            symbol2index.emplace(transition_signal, alphabet_size);
            transition_signal_index = alphabet_size;
            ++alphabet_size;
        } else {
            transition_signal_index = found->second;
        }
        delta.at(from).resize(alphabet_size);
        delta.at(from).at(transition_signal_index).push_back(to);
    }

    vector<bool> final(states_count);
    for (uint64_t i = 0; i < states_count; ++i) {
        delta.at(i).resize(alphabet_size);

        int is_final;
        std::cin >> is_final;
        final.at(i) = is_final;
    }

    uint64_t q0;
    std::cin >> q0;

    vector<string> alphabet(symbol2index.size());
    for (const auto &[symbol, index] : symbol2index) {
        alphabet.at(index) = symbol;
    }

    const auto [det_delta, det_final, state_index2label] =
        det(delta, final, q0);

    print_table(alphabet, det_delta, state_index2label);

    for (size_t col_i = LAMBDA_INDEX + 1; col_i < alphabet.size(); ++col_i) {
        vector<string> eq{};
        for (size_t next_col_i = col_i + 1; next_col_i < alphabet.size();
             ++next_col_i) {
            bool cur_eq_next = true;
            for (const auto &row : det_delta) {
                if (*row.at(col_i) != *row.at(next_col_i)) {
                    cur_eq_next = false;
                    break;
                }
            }
            if (cur_eq_next) {
                eq.push_back(alphabet.at(next_col_i));
            }
        }
        cout << alphabet.at(col_i) << " is equivalent to " << vect2string(eq)
             << '\n';
    }

    print_automaton(alphabet, det_delta, det_final, state_index2label);
}
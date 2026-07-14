const lexicon = {
  love: 3.2, loved: 3.2, like: 1.5, amazing: 3.2, awesome: 3.1, wonderful: 3,
  excellent: 3.2, perfect: 3.1, fantastic: 3.2, great: 2.5, good: 1.9, happy: 2.7,
  joy: 2.8, excited: 2.4, beautiful: 2.5, helpful: 1.8, thanks: 1.5, thank: 1.5,
  pleased: 2.1, win: 2.3, best: 3, brilliant: 2.8, recommend: 2.1, easy: 1.5,
  enjoy: 2.2, calm: 1.5, hope: 1.7, hate: -3.3, hated: -3.3, awful: -3.1,
  terrible: -3.2, horrible: -3.2, worst: -3.4, bad: -2.2, sad: -2.3, angry: -2.7,
  disappointed: -2.6, disappointing: -2.6, broken: -2.1, fail: -2.4, failed: -2.4,
  failure: -2.6, useless: -2.5, annoying: -1.9, problem: -1.6, wrong: -1.7,
  never: -1.1, nothing: -1.2, difficult: -1.3, poor: -2, upset: -2.1,
  frustrated: -2, regret: -2.2, pain: -2.1, lonely: -2.4, hopeless: -3.1,
  exhausted: -1.8, empty: -1.7, worthless: -3.2,
};
const intensifiers = new Set(["very", "really", "extremely", "absolutely", "so", "incredibly", "deeply", "totally"]);
const negators = new Set(["not", "no", "never", "hardly", "isnt", "wasnt", "dont", "didnt", "cant", "cannot", "wont"]);
const distressTerms = {
  depressed: 3, depression: 3, hopeless: 3, worthless: 3, suicide: 5, suicidal: 5,
  die: 4, dying: 4, "kill myself": 6, "end my life": 6, alone: 2, lonely: 2,
  empty: 2, exhausted: 1.5, trapped: 2.5, unbearable: 3, pointless: 2.5,
  "give up": 3, "no reason": 2.5, numb: 2, "cannot go on": 5,
};

const tokenize = (text) => text.toLowerCase().replace(/[’']/g, "").match(/[a-z]+|[!?]+/g) || [];

export function analyzePolarity(text) {
  const tokens = tokenize(text);
  let positiveValue = 0;
  let negativeValue = 0;
  const hits = [];
  tokens.forEach((word, index) => {
    if (!(word in lexicon)) return;
    let value = lexicon[word];
    if (intensifiers.has(tokens[index - 1])) value *= 1.45;
    if (negators.has(tokens[index - 1]) || negators.has(tokens[index - 2])) value *= -0.8;
    if (value > 0) positiveValue += value;
    else negativeValue += Math.abs(value);
    hits.push({ word, value });
  });
  const emphasis = Math.min((text.match(/!/g) || []).length * 0.35, 1.4);
  if (emphasis && (positiveValue || negativeValue)) {
    if (positiveValue >= negativeValue) positiveValue += emphasis;
    else negativeValue += emphasis;
  }
  let neutralValue = Math.max(1.2, tokens.length * 0.12);
  if (!positiveValue && !negativeValue) neutralValue = Math.max(4, tokens.length * 0.3);
  const total = positiveValue + negativeValue + neutralValue;
  const positive = Math.round((positiveValue / total) * 100);
  const negative = Math.round((negativeValue / total) * 100);
  const scores = { positive, neutral: 100 - positive - negative, negative };
  const label = Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0];
  const cues = hits.sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 4).map(({ word }) => word);
  return { scores, label, cues, confidence: scores[label] };
}

export function analyzeDistress(text) {
  const lower = text.toLowerCase();
  let weighted = 0;
  const cues = [];
  Object.entries(distressTerms).forEach(([term, weight]) => {
    if (lower.includes(term)) { weighted += weight; cues.push(term); }
  });
  const base = analyzePolarity(text);
  weighted += Math.max(0, base.scores.negative - 30) / 18;
  const risk = Math.min(96, Math.round(8 + weighted * 10));
  const scores = { supportive: 100 - risk, distress: risk };
  const label = risk >= 50 ? "distress" : "supportive";
  return { scores, label, cues: [...new Set(cues)].slice(0, 5), confidence: Math.max(risk, 100 - risk) };
}

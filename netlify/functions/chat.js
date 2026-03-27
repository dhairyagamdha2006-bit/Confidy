exports.handler = async function(event) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }
  try {
    const body = JSON.parse(event.body || "{}");
    if (body.scoreOnly) {
      const scores = scoreMessages(body.messages || [], body.scenario || "approach");
      return { statusCode: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }, body: JSON.stringify(scores) };
    }
    const { messages, system } = body;
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-api-key": process.env.ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({ model: "claude-sonnet-4-20250514", max_tokens: 1000, system, messages })
    });
    const data = await response.json();
    return { statusCode: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }, body: JSON.stringify(data) };
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};

function scoreMessages(messages, scenario) {
  const userMessages = messages.filter(m => m.role === "user" && !m.content.startsWith("[SYSTEM")).map(m => m.content.toLowerCase().trim());
  if (!userMessages.length) return { opening: 15, flow: 8, rejection: 5, mindset: 20, overall: 12 };
  const opening = scoreOpeningLines(userMessages);
  const flow = scoreConversationFlow(userMessages);
  const rejection = scoreRejectionResilience(userMessages, scenario);
  const mindset = scoreMindsetFrame(userMessages);
  const overall = Math.round((opening + flow + rejection + mindset) / 4);
  return { opening, flow, rejection, mindset, overall };
}

function scoreOpeningLines(messages) {
  const first = messages[0] || "";
  let score = 20;
  if (first.includes("?")) score += 20;
  if (first.includes("you") || first.includes("your")) score += 15;
  if (first.split(" ").length >= 5) score += 10;
  if (first.split(" ").length <= 25) score += 10;
  if (["notice","noticed","saw","love","like","interesting"].some(w => first.includes(w))) score += 10;
  if (["hey","hi","excuse me","sorry to"].some(w => first.includes(w))) score += 5;
  const weakOpeners = ["um","uh","so i was","i don't know","maybe"];
  score -= weakOpeners.filter(w => first.includes(w)).length * 8;
  if (first.split(" ").length < 3) score -= 20;
  if (["hey","hi","hello","sup","hey there"].includes(first.trim())) score -= 15;
  return Math.max(0, Math.min(100, score));
}

function scoreConversationFlow(messages) {
  if (messages.length < 2) return 10;
  let score = 30;
  const questionCount = messages.filter(m => m.includes("?")).length;
  const ratio = questionCount / messages.length;
  if (ratio >= 0.3 && ratio <= 0.7) score += 25;
  else if (ratio < 0.2) score -= 10;
  else if (ratio > 0.8) score -= 5;
  const followUpWords = ["tell me more","what do you","how did","why did","what about","really?","interesting"];
  const followUps = messages.reduce((acc, m) => acc + followUpWords.filter(w => m.includes(w)).length, 0);
  score += Math.min(20, followUps * 7);
  const selfWords = ["i also","me too","same here","i love","i think","i feel"];
  const selfDisc = messages.reduce((acc, m) => acc + selfWords.filter(w => m.includes(w)).length, 0);
  score += Math.min(15, selfDisc * 5);
  const shortMsgs = messages.filter(m => m.split(" ").length < 4).length;
  score -= shortMsgs * 5;
  return Math.max(0, Math.min(100, score));
}

function scoreRejectionResilience(messages, scenario) {
  const allText = messages.join(" ");
  if (scenario !== "rejection") {
    let score = 40;
    const confidentPhrases = ["i will","i want to","let me","i am","i can","definitely","absolutely"];
    const nervousPhrases = ["what if they","what if i","scared","nervous","afraid","worried"];
    score += Math.min(30, confidentPhrases.filter(p => allText.includes(p)).length * 8);
    score -= Math.min(30, nervousPhrases.filter(p => allText.includes(p)).length * 8);
    return Math.max(0, Math.min(100, score));
  }
  let score = 20;
  const growthWords = ["learn","data","practice","next time","okay","fine","move on","try again","experience"];
  const catastropheWords = ["ruined","terrible","worst","never","always","hate myself","hopeless","give up"];
  score += Math.min(40, growthWords.filter(w => allText.includes(w)).length * 8);
  score -= Math.min(30, catastropheWords.filter(w => allText.includes(w)).length * 10);
  const avgLen = messages.reduce((a, m) => a + m.split(" ").length, 0) / messages.length;
  if (avgLen > 15) score += 20;
  else if (avgLen > 8) score += 10;
  return Math.max(0, Math.min(100, score));
}

function scoreMindsetFrame(messages) {
  const allText = messages.join(" ");
  let score = 30;
  const powerWords = ["i want","i will","let us","let's","i decided","absolutely","definitely","for sure"];
  const weakWords = ["i can't","i could not","maybe","kind of","sort of","i guess","i just","i hope they"];
  const fillers = [" um "," uh "," like "," literally "," basically "];
  score += Math.min(30, powerWords.filter(w => allText.includes(w)).length * 6);
  score -= Math.min(30, weakWords.filter(w => allText.includes(w)).length * 6);
  const fillerCount = fillers.reduce((acc, f) => acc + (allText.split(f).length - 1), 0);
  score -= Math.min(20, fillerCount * 4);
  const avgWords = messages.reduce((a, m) => a + m.split(" ").length, 0) / messages.length;
  if (avgWords >= 12) score += 15;
  else if (avgWords >= 7) score += 8;
  return Math.max(0, Math.min(100, score));
}

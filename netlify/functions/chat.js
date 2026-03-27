exports.handler = async function(event) {
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
      body: JSON.stringify({ error: { message: "Method Not Allowed" } })
    };
  }

  try {
    const parsed = JSON.parse(event.body || "{}");
    const messages = Array.isArray(parsed.messages) ? parsed.messages : [];
    const system = typeof parsed.system === "string" ? parsed.system : "";

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY || "KEY_NOT_FOUND",
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1000,
        system,
        messages
      })
    });

    const data = await response.json().catch(function() {
      return { error: { message: "Invalid JSON returned by AI provider" } };
    });

    return {
      statusCode: response.status,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
      body: JSON.stringify(data)
    };
  } catch (err) {
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
      body: JSON.stringify({
        error: {
          message: err && err.message ? err.message : "Unexpected server error"
        }
      })
    };
  }
};

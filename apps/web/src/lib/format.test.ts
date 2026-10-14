import { describe, expect, it } from "vitest";
import { formatWinPercentage } from "@/lib/format";

describe("formatWinPercentage", () => {
  it("returns Russian label for null", () => {
    expect(formatWinPercentage(null)).toBe("Нет данных");
    expect(formatWinPercentage(undefined)).toBe("Нет данных");
  });

  it("formats numeric percentage", () => {
    expect(formatWinPercentage(100)).toBe("100.0%");
    expect(formatWinPercentage(66.666)).toBe("66.7%");
  });
});

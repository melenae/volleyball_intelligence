import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorBlock } from "@/components/ui/async-state";
import { ApiError } from "@/lib/api-client";

describe("ErrorBlock", () => {
  it("shows API error message for 404", () => {
    render(
      <ErrorBlock error={new ApiError(404, "not_found", "Команда не найдена.")} />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Команда не найдена.");
  });
});

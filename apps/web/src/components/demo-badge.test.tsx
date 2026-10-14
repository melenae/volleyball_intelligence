import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DemoBadge } from "@/components/demo-badge";

describe("DemoBadge", () => {
  it("renders for demo origin", () => {
    render(<DemoBadge dataOrigin="demo" />);
    expect(screen.getByRole("status")).toHaveTextContent("Демонстрационные данные");
  });

  it("renders nothing for other origins", () => {
    const { container } = render(<DemoBadge />);
    expect(container).toBeEmptyDOMElement();
  });
});

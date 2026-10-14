import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PaginationControls } from "@/components/ui/pagination-controls";

describe("PaginationControls", () => {
  it("calls onPageChange with next offset", () => {
    const onPageChange = vi.fn();
    render(
      <PaginationControls
        pagination={{ limit: 10, offset: 0, total: 25 }}
        onPageChange={onPageChange}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Вперёд" }));
    expect(onPageChange).toHaveBeenCalledWith(10);
  });

  it("renders nothing for single page", () => {
    const { container } = render(
      <PaginationControls
        pagination={{ limit: 20, offset: 0, total: 5 }}
        onPageChange={() => undefined}
      />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});

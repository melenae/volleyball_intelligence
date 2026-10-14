type Props = {
  title: string;
  description?: string;
};

export function PageHeader({ title, description }: Props) {
  return (
    <header className="flex flex-col gap-2">
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      {description ? <p className="max-w-3xl text-muted">{description}</p> : null}
    </header>
  );
}

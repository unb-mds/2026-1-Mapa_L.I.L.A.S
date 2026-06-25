export default function BotaoExportar({ chartRef, nomeArquivo = 'grafico-lilas' }) {
  const exportarPNG = () => {
    if (!chartRef?.current) return;

    const svg = chartRef.current.querySelector('svg');
    if (!svg) return;

    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      canvas.width = img.width || 800;
      canvas.height = img.height || 400;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);

      const link = document.createElement('a');
      link.download = `${nomeArquivo}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    };

    img.src = url;
  };

  return (
    <button
      onClick={exportarPNG}
      className="flex items-center gap-2 px-4 py-1.5 text-sm font-semibold text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
    >
      ⬇ EXPORTAR
    </button>
  );
}
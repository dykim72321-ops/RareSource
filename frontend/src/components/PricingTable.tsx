import React from 'react';

interface PricingRow {
  distributor: string;
  sku: string;
  stock: number;
  moq: number;
  price_1: number;
  price_10: number;
  price_100: number;
  price_1000: number;
  currency: string;
  lastUpdated: string;
  url?: string;
}

interface PricingTableProps {
  data: PricingRow[];
}

const PricingTable: React.FC<PricingTableProps> = ({ data }) => {
  const formatTime = (timestamp: string) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return '<1m ago';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <div className="pricing-table-wrapper">
      <table className="pricing-table">
        <thead>
          <tr>
            <th>Distributor</th>
            <th>SKU</th>
            <th>Stock</th>
            <th>MOQ</th>
            <th>1 Unit</th>
            <th>10 Units</th>
            <th>100 Units</th>
            <th>1000 Units</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td>
                <div className="distributor-name">
                  {row.distributor}
                </div>
              </td>
              <td style={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                {row.sku}
              </td>
              <td className={row.stock > 0 ? 'stock-available' : 'stock-unavailable'}>
                {row.stock > 0 ? row.stock.toLocaleString() : 'Check'}
              </td>
              <td>{row.moq}</td>
              <td className="price-tier">
                {row.price_1 > 0 ? `${row.currency}${row.price_1.toLocaleString()}` : '-'}
              </td>
              <td className="price-tier">
                {row.price_10 > 0 ? `${row.currency}${row.price_10.toLocaleString()}` : '-'}
              </td>
              <td className="price-tier">
                {row.price_100 > 0 ? `${row.currency}${row.price_100.toLocaleString()}` : '-'}
              </td>
              <td className="price-tier">
                {row.price_1000 > 0 ? `${row.currency}${row.price_1000.toLocaleString()}` : '-'}
              </td>
              <td className="last-updated">
                {formatTime(row.lastUpdated)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PricingTable;

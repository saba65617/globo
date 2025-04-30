# Missing Migrants Analysis Dashboard

A Streamlit dashboard analyzing global data on missing and deceased migrants between 2014 and 2024. The dashboard provides interactive visualizations and insights into migrant deaths, affected regions, common causes, and incident locations.

## Features

- Interactive data filtering by year, region, and cause of death
- Multiple visualization types including:
  - Yearly trends
  - Regional analysis
  - Causes of death
  - Demographics analysis
  - Geographic distribution
- Modern UI with responsive design
- Real-time data updates

## Local Development

1. Clone the repository:
```bash
git clone <your-repository-url>
cd MigrantTrackingDashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Update the Supabase credentials in `.env`

4. Run the application:
```bash
streamlit run app.py
```

## Deployment

### Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Deploy the application

### Environment Variables

Make sure to set these environment variables in your deployment platform:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase project API key

## Data Source

The dashboard uses the Global Missing Migrants Dataset, which tracks deaths of migrants, including refugees and asylum-seekers, who have died or gone missing in the process of migration towards an international destination.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
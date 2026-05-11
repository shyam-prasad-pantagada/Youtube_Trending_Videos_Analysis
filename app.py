"""
YouTube Trending Videos Analysis - Flask Backend with Dynamic Data
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import os
import random
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ============================================
# YOUTUBE ANALYZER CLASS WITH DYNAMIC DATA
# ============================================

class YouTubeAnalyzer:
    def __init__(self):
        self.df = None
        self.csv_path = 'youtube_trending_data.csv'
        self.last_update = None
        
    def create_dataset(self):
        """Create comprehensive YouTube trending dataset"""
        
        categories = ['Technology', 'Entertainment', 'Education', 'Fitness', 
                     'Gaming', 'Cooking', 'Music', 'News', 'Travel', 'Lifestyle']
        regions = ['US', 'UK', 'India', 'Canada', 'Australia', 'Germany', 
                  'Brazil', 'Japan', 'France', 'South Korea']
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Video titles templates
        title_templates = {
            'Technology': ['Review', 'Unboxing', 'Tutorial', 'News', 'Comparison'],
            'Entertainment': ['Funny', 'Reaction', 'Compilation', 'Challenge', 'Prank'],
            'Education': ['Learn', 'Guide', 'Course', 'Tips', 'Explained'],
            'Fitness': ['Workout', 'Exercise', 'Diet', 'Training', 'Fitness'],
            'Gaming': ['Gameplay', 'Stream', 'Review', 'Highlights', 'Walkthrough'],
            'Cooking': ['Recipe', 'Cooking', 'Baking', 'Meal Prep', 'Kitchen'],
            'Music': ['Song', 'Performance', 'Cover', 'Remix', 'Concert'],
            'News': ['Breaking', 'Update', 'Report', 'Analysis', 'Coverage'],
            'Travel': ['Vlog', 'Guide', 'Adventure', 'Trip', 'Travel'],
            'Lifestyle': ['Routine', 'Hacks', 'Tips', 'Lifestyle', 'Vlog']
        }
        
        data = []
        for i in range(1, 301):  # 300 videos for more dynamic data
            category = random.choice(categories)
            template = random.choice(title_templates[category])
            title = f"{category} {template} {i} - 2024"
            
            # Dynamic view counts with trends
            base_views = random.randint(50000, 5000000)
            # Add some trending variation
            if random.random() > 0.7:  # 30% are viral
                views = base_views * random.randint(5, 20)
            else:
                views = base_views
            
            likes = int(views * random.uniform(0.03, 0.18))
            comments = int(views * random.uniform(0.002, 0.06))
            
            # Add time-based trends
            hour = random.randint(0, 23)
            # Peak hours (6-9 PM) get more views
            if 18 <= hour <= 21:
                views = int(views * 1.3)
            
            data.append({
                'video_id': f'VID{i:04d}',
                'title': title,
                'category': category,
                'region': random.choice(regions),
                'views': views,
                'likes': likes,
                'comments': comments,
                'duration_min': random.randint(3, 45),
                'publish_hour': hour,
                'publish_day': random.choice(days),
                'trending_score': random.randint(1, 100)
            })
        
        self.df = pd.DataFrame(data)
        self.calculate_metrics()
        self.df.to_csv(self.csv_path, index=False)
        self.last_update = datetime.now()
        return self.df
    
    def load_data(self):
        """Load data from CSV or create new"""
        if os.path.exists(self.csv_path):
            self.df = pd.read_csv(self.csv_path)
            # Check if data is older than 1 hour, regenerate if needed
            file_time = datetime.fromtimestamp(os.path.getmtime(self.csv_path))
            if (datetime.now() - file_time).seconds > 3600:
                print("🔄 Data is old, regenerating...")
                self.df = self.create_dataset()
        else:
            self.df = self.create_dataset()
        
        self.calculate_metrics()
        return self.df
    
    def calculate_metrics(self):
        """Calculate engagement metrics"""
        df = self.df
        df['engagement_rate'] = ((df['likes'] + df['comments']) / df['views'] * 100).round(2)
        df['like_ratio'] = (df['likes'] / df['views'] * 100).round(2)
        df['comment_ratio'] = (df['comments'] / df['views'] * 100).round(2)
        
        # Performance categories
        df['performance'] = pd.cut(df['views'], 
                                   bins=[0, 100000, 500000, 1000000, 5000000, float('inf')],
                                   labels=['Low', 'Medium', 'High', 'Viral', 'Trending'])
        
        # Time categorization
        df['time_of_day'] = pd.cut(df['publish_hour'], 
                                   bins=[-1, 6, 12, 18, 24], 
                                   labels=['Night', 'Morning', 'Afternoon', 'Evening'])
        
        self.df = df
    
    def get_dynamic_statistics(self):
        """Get all statistics with dynamic updates"""
        df = self.df
        
        # Category trends
        category_stats = df.groupby('category').agg({
            'views': ['mean', 'sum', 'count'],
            'engagement_rate': 'mean',
            'likes': 'mean'
        }).round(2)
        
        # Top performing categories
        top_categories = df.groupby('category')['views'].mean().sort_values(ascending=False).head(5)
        
        # Regional trends
        region_stats = df.groupby('region').agg({
            'views': ['sum', 'mean'],
            'engagement_rate': 'mean'
        }).round(2)
        
        # Hourly trends
        hourly_trends = df.groupby('publish_hour')['views'].mean().to_dict()
        
        # Daily trends
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_trends = df.groupby('publish_day')['views'].mean().reindex(day_order).to_dict()
        
        # Trending now (top 10 by views)
        trending_now = df.nlargest(10, 'views')[
            ['title', 'category', 'region', 'views', 'likes', 'engagement_rate', 'trending_score']
        ].to_dict('records')
        
        # Format trending videos
        trending_list = []
        for v in trending_now:
            trending_list.append({
                'title': v['title'],
                'category': v['category'],
                'region': v['region'],
                'views': f"{v['views']:,}",
                'likes': f"{v['likes']:,}",
                'engagement': f"{v['engagement_rate']}%",
                'trending_score': v['trending_score']
            })
        
        # Summary with dynamic metrics
        summary = {
            'total_videos': len(df),
            'total_views': f"{df['views'].sum():,}",
            'avg_views': f"{int(df['views'].mean()):,}",
            'avg_engagement': f"{df['engagement_rate'].mean():.1f}%",
            'best_category': df.groupby('category')['views'].mean().idxmax(),
            'best_region': df.groupby('region')['views'].sum().idxmax(),
            'best_hour': int(df.groupby('publish_hour')['views'].mean().idxmax()),
            'best_day': df.groupby('publish_day')['views'].mean().idxmax(),
            'viral_count': len(df[df['views'] > 1000000]),
            'total_likes': f"{df['likes'].sum():,}",
            'avg_duration': int(df['duration_min'].mean())
        }
        
        # Time series data for charts
        time_series = {
            'hourly': {str(k): float(v) for k, v in hourly_trends.items()},
            'daily': daily_trends,
            'categories': df['category'].value_counts().to_dict(),
            'regions': df['region'].value_counts().to_dict()
        }
        
        return {
            'summary': summary,
            'categories': sorted(df['category'].unique().tolist()),
            'regions': sorted(df['region'].unique().tolist()),
            'trending_now': trending_list,
            'time_series': time_series,
            'last_update': self.last_update.isoformat() if self.last_update else datetime.now().isoformat()
        }
    
    def get_filtered_data(self, filters):
        """Get filtered data with dynamic updates"""
        filtered = self.df.copy()
        
        if filters.get('category') and filters['category'] != 'all':
            filtered = filtered[filtered['category'] == filters['category']]
        
        if filters.get('region') and filters['region'] != 'all':
            filtered = filtered[filtered['region'] == filters['region']]
        
        if filters.get('minViews'):
            filtered = filtered[filtered['views'] >= int(filters['minViews'])]
        
        if filters.get('maxViews'):
            filtered = filtered[filtered['views'] <= int(filters['maxViews'])]
        
        if filters.get('minEngagement'):
            filtered = filtered[filtered['engagement_rate'] >= float(filters['minEngagement'])]
        
        if filters.get('sortBy'):
            if filters['sortBy'] == 'views':
                filtered = filtered.sort_values('views', ascending=False)
            elif filters['sortBy'] == 'engagement':
                filtered = filtered.sort_values('engagement_rate', ascending=False)
            elif filters['sortBy'] == 'likes':
                filtered = filtered.sort_values('likes', ascending=False)
        
        # Get top results
        filtered = filtered.head(30)
        
        result = []
        for _, row in filtered.iterrows():
            result.append({
                'title': row['title'],
                'category': row['category'],
                'region': row['region'],
                'views': f"{row['views']:,}",
                'likes': f"{row['likes']:,}",
                'engagement': f"{row['engagement_rate']}%",
                'trending_score': row.get('trending_score', 50)
            })
        
        return result
    
    def get_chart_data(self, chart_type):
        """Get raw chart data for dynamic visualization"""
        df = self.df
        
        if chart_type == 'category':
            data = df.groupby('category')['views'].mean().sort_values(ascending=False).head(8)
            return {
                'labels': data.index.tolist(),
                'values': data.values.tolist(),
                'title': 'Average Views by Category'
            }
        
        elif chart_type == 'region':
            data = df.groupby('region')['views'].sum().sort_values(ascending=False).head(8)
            return {
                'labels': data.index.tolist(),
                'values': data.values.tolist(),
                'title': 'Total Views by Region'
            }
        
        elif chart_type == 'hourly':
            hourly = df.groupby('publish_hour')['views'].mean()
            return {
                'labels': [f"{h}:00" for h in range(24)],
                'values': [float(hourly.get(h, 0)) for h in range(24)],
                'title': 'Average Views by Hour'
            }
        
        elif chart_type == 'engagement':
            data = df.groupby('category')['engagement_rate'].mean().sort_values(ascending=False).head(8)
            return {
                'labels': data.index.tolist(),
                'values': data.values.tolist(),
                'title': 'Engagement Rate by Category'
            }
        
        elif chart_type == 'trending':
            trending = df.nlargest(10, 'views')[['title', 'views']]
            return {
                'labels': [t[:20] + '...' if len(t) > 20 else t for t in trending['title'].tolist()],
                'values': trending['views'].tolist(),
                'title': 'Top 10 Trending Videos'
            }
        
        elif chart_type == 'performance':
            perf = df['performance'].value_counts()
            return {
                'labels': perf.index.tolist(),
                'values': perf.values.tolist(),
                'title': 'Video Performance Distribution'
            }
        
        elif chart_type == 'duration':
            duration_stats = df.groupby(pd.cut(df['duration_min'], 
                                              bins=[0,5,10,15,20,30,60]))['views'].mean()
            return {
                'labels': ['0-5', '5-10', '10-15', '15-20', '20-30', '30-60'],
                'values': duration_stats.values.tolist(),
                'title': 'Views by Duration (minutes)'
            }
        
        return {'labels': [], 'values': [], 'title': 'No Data'}

# Initialize analyzer
analyzer = YouTubeAnalyzer()
analyzer.load_data()

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'videos': len(analyzer.df),
        'last_update': analyzer.last_update.isoformat() if analyzer.last_update else None
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = analyzer.get_dynamic_statistics()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chart-data/<chart_type>', methods=['GET'])
def get_chart_data(chart_type):
    """Get raw chart data for dynamic frontend charts"""
    try:
        chart_data = analyzer.get_chart_data(chart_type)
        return jsonify({'success': True, 'data': chart_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/filter', methods=['POST'])
def filter_videos():
    try:
        filters = request.json
        filtered = analyzer.get_filtered_data(filters)
        return jsonify({'success': True, 'data': filtered})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Force refresh data"""
    try:
        analyzer.df = analyzer.create_dataset()
        analyzer.last_update = datetime.now()
        return jsonify({'success': True, 'message': 'Data refreshed', 'time': analyzer.last_update.isoformat()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    csv_data = analyzer.df.to_csv(index=False)
    return send_file(
        io.BytesIO(csv_data.encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'youtube_dynamic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📺 YOUTUBE TRENDING ANALYSIS - DYNAMIC BACKEND")
    print("="*70)
    print(f"\n📊 Videos: {len(analyzer.df)}")
    print(f"📁 CSV: {analyzer.csv_path}")
    print(f"🔄 Dynamic updates: Every request gets fresh calculations")
    print(f"\n🚀 Server: http://127.0.0.1:5000")
    print("\n📡 Dynamic Endpoints:")
    print("   /api/statistics - Live stats")
    print("   /api/chart-data/<type> - Raw chart data")
    print("   /api/filter - Dynamic filtering")
    print("   /api/refresh - Force data refresh")
    print("\n" + "="*70)
    app.run(debug=True, host='127.0.0.1', port=5000)
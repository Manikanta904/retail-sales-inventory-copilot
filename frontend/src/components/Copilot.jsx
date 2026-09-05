import React, { useState, useEffect, useRef } from 'react';
import { queryCopilot } from '../api/api';
import ChatMessage from './ChatMessage';
import { Send, Sparkles, Filter, Trash2, RefreshCw } from 'lucide-react';

export default function Copilot({ stores = [], products = [], initialQuestion = '' }) {
  const [question, setQuestion] = useState('');
  const [storeId, setStoreId] = useState('');
  const [productId, setProductId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [lastSubmittedQuery, setLastSubmittedQuery] = useState('');

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      response: {
        status: 'success',
        answer:
          'Welcome to the Retail Sales and Inventory Copilot. I can assist with inventory coverage, predicted stock-out risks, overstocked items, sales spikes, sales drops, and product performance summaries grounded in your retail dataset.',
        findings: [
          'Ask questions about stockouts, overstock, sales trends, or store performance.',
          'Select optional store or product filters if targeting specific catalog items.',
        ],
        data_sources: ['stores.csv', 'products.csv', 'sales.csv', 'inventory.csv', 'rule_documents'],
      },
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState('Analyzing retail data...');
  const chatEndRef = useRef(null);
  const handledInitialRef = useRef('');

  useEffect(() => {
    if (typeof initialQuestion === 'string' && initialQuestion.trim() && initialQuestion !== handledInitialRef.current) {
      handledInitialRef.current = initialQuestion;
      setQuestion(initialQuestion);
      executeQuery(initialQuestion);
    }
  }, [initialQuestion]);

  useEffect(() => {
    let timer1, timer2;
    if (loading) {
      setLoadingStage('Analyzing retail data...');
      timer1 = setTimeout(() => setLoadingStage('Evaluating business rules...'), 2000);
      timer2 = setTimeout(() => setLoadingStage('Generating grounded response...'), 5000);
    }
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [loading]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSuggestedClick = (text) => {
    setQuestion(text);
  };

  const executeQuery = async (queryText) => {
    const qTrimmed = queryText.trim();
    if (!qTrimmed || loading) return;

    setLastSubmittedQuery(qTrimmed);

    // Add User Message if not already present
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      if (last && last.role === 'user' && last.content === qTrimmed) {
        return prev;
      }
      return [...prev, { role: 'user', content: qTrimmed }];
    });

    setQuestion('');
    setLoading(true);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 55000);

    try {
      const payload = {
        question: qTrimmed,
        store_id: storeId || undefined,
        product_id: productId || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      };

      const res = await queryCopilot(payload, { signal: controller.signal });
      clearTimeout(timeoutId);
      setMessages((prev) => [...prev, { role: 'assistant', response: res }]);
    } catch (err) {
      clearTimeout(timeoutId);
      const isTimeout = err.name === 'AbortError' || (err.message && err.message.includes('abort'));
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          response: {
            status: 'insufficient_data',
            answer: isTimeout
              ? 'The analysis is taking longer than expected. Please try again.'
              : err.message || 'Error processing request.',
            missing_information: [isTimeout ? 'Timely reasoning response from backend' : 'Backend connection'],
            available_information: ['Retry your query or check http://127.0.0.1:8000/api/health'],
            isTimeoutError: isTimeout,
          },
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    executeQuery(question);
  };

  const handleRetry = () => {
    if (lastSubmittedQuery) {
      executeQuery(lastSubmittedQuery);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const suggestedQueries = [
    'What products are likely to run out?',
    'Which products are overstocked?',
    'Which products have unusual sales spikes or drops?',
    'How did the Wireless Ergonomic Mouse perform this month?',
    'Did competitor pricing cause the sales drop?',
  ];

  return (
    <div className="copilot-container">
      {/* Intro Card with Suggested Query Chips */}
      <div className="copilot-intro-card">
        <div className="section-title">
          <Sparkles className="text-primary" size={20} /> Retail Reasoning Copilot
        </div>
        <p className="page-desc" style={{ marginTop: '0.25rem' }}>
          Grounds reasoning in deterministic Python analytics and local retail business rules using official Gemini models.
        </p>

        <div className="suggested-queries">
          {suggestedQueries.map((qText, idx) => (
            <button
              key={idx}
              className="query-chip"
              onClick={() => handleSuggestedClick(qText)}
            >
              {qText}
            </button>
          ))}
        </div>
      </div>

      {/* Optional Filters Bar Toggle */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          className="nav-btn"
          onClick={() => setShowFilters(!showFilters)}
          style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}
        >
          <Filter size={16} /> {showFilters ? 'Hide Target Filters' : 'Show Optional Target Filters'}
        </button>

        {messages.length > 0 && (
          <button className="nav-btn" onClick={handleClearChat} title="Clear Chat Log">
            <Trash2 size={16} /> Clear Chat
          </button>
        )}
      </div>

      {/* Target Filters Drawer */}
      {showFilters && (
        <div className="filters-bar">
          <div className="filter-group">
            <label className="filter-label">Store Filter</label>
            <select
              className="select-input"
              value={storeId}
              onChange={(e) => setStoreId(e.target.value)}
            >
              <option value="">All Stores (All Network)</option>
              {stores.map((s) => (
                <option key={s.store_id} value={s.store_id}>
                  {s.store_id} - {s.store_name}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Product Filter</label>
            <select
              className="select-input"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
            >
              <option value="">All Products (Entire Catalog)</option>
              {products.map((p) => (
                <option key={p.product_id} value={p.product_id}>
                  {p.product_id} - {p.product_name}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Start Date</label>
            <input
              type="date"
              className="date-input"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="filter-group">
            <label className="filter-label">End Date</label>
            <input
              type="date"
              className="date-input"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>
      )}

      {/* Chat Messages Log */}
      <div className="chat-log">
        {messages.map((msg, idx) => (
          <React.Fragment key={idx}>
            <ChatMessage message={msg} />
            {msg.response?.isTimeoutError && (
              <div style={{ marginTop: '-0.5rem', marginLeft: '3.5rem' }}>
                <button
                  className="nav-btn active"
                  onClick={handleRetry}
                  disabled={loading}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
                >
                  <RefreshCw size={14} /> Retry Query
                </button>
              </div>
            )}
          </React.Fragment>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="avatar assistant">
              <Sparkles size={20} />
            </div>
            <div className="message-bubble" style={{ minWidth: 240 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                <div className="loading-spinner" style={{ borderColor: 'var(--primary)', borderTopColor: 'transparent' }}></div>
                <span>{loadingStage}</span>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Query Form Bar */}
      <form onSubmit={handleSubmit} className="query-form">
        <textarea
          className="query-textarea"
          rows={2}
          placeholder="Ask the retail copilot about stockouts, overstock, sales spikes, or store performance..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button type="submit" className="submit-btn" disabled={!question.trim() || loading}>
          {loading ? (
            <span className="loading-spinner"></span>
          ) : (
            <>
              <Send size={16} /> Submit Query
            </>
          )}
        </button>
      </form>
    </div>
  );
}

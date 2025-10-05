# 🙏 Model Credits and Attribution

This application uses several open-source AI models from HuggingFace. We are grateful to the researchers and organizations who made these models available:

---

## 🤖 AI Models Used

### 1. **FinBERT** - Financial Sentiment Analysis
- **Model**: `yiyanghkust/finbert-tone`
- **Created by**: Yi Yang, University of Hong Kong
- **Purpose**: Analyzes sentiment of financial news articles
- **License**: Apache 2.0
- **Paper**: [FinBERT: Financial Sentiment Analysis with Pre-trained Language Models](https://arxiv.org/abs/1908.10063)
- **HuggingFace**: https://huggingface.co/yiyanghkust/finbert-tone

**Citation:**
```
@article{yang2020finbert,
  title={FinBERT: Financial Sentiment Analysis with Pre-trained Language Models},
  author={Yang, Yi and UY, Mark Christopher Siy and Huang, Allen},
  journal={arXiv preprint arXiv:1908.10063},
  year={2020}
}
```

---

### 2. **Twitter-RoBERTa** - Social Media Sentiment
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Created by**: Cardiff NLP, Cardiff University
- **Purpose**: Analyzes sentiment of social media posts and tweets
- **License**: MIT
- **Paper**: [TweetEval: Unified Benchmark and Comparative Evaluation](https://arxiv.org/abs/2010.12421)
- **HuggingFace**: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest

**Citation:**
```
@inproceedings{barbieri2020tweeteval,
  title={TweetEval: Unified Benchmark and Comparative Evaluation for Tweet Classification},
  author={Barbieri, Francesco and Camacho-Collados, Jose and Espinosa Anke, Luis and Neves, Leonardo},
  booktitle={Findings of EMNLP},
  year={2020}
}
```

---

### 3. **DistilBERT** - Question Answering
- **Model**: `distilbert-base-cased-distilled-squad`
- **Created by**: HuggingFace & Google Research
- **Purpose**: Powers the AI chat assistant for stock Q&A
- **License**: Apache 2.0
- **Paper**: [DistilBERT, a distilled version of BERT](https://arxiv.org/abs/1910.01108)
- **HuggingFace**: https://huggingface.co/distilbert-base-cased-distilled-squad

**Citation:**
```
@article{sanh2019distilbert,
  title={DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter},
  author={Sanh, Victor and Debut, Lysandre and Chaumond, Julien and Wolf, Thomas},
  journal={arXiv preprint arXiv:1910.01108},
  year={2019}
}
```

---

## 📊 Data Sources

### **Yahoo Finance** (via yfinance)
- Stock prices, historical data, and news
- **Library**: https://github.com/ranaroussi/yfinance
- **License**: Apache 2.0

### **CoinGecko API**
- Cryptocurrency prices and market data
- **Website**: https://www.coingecko.com
- **API Docs**: https://www.coingecko.com/en/api
- **License**: Free tier (non-commercial use)

---

## 🔧 Technical Frameworks

### **Transformers** by HuggingFace
- **Library**: https://github.com/huggingface/transformers
- **License**: Apache 2.0
- Powers all AI model loading and inference

### **PyTorch**
- **Library**: https://pytorch.org
- **License**: BSD
- Deep learning framework for AI models

### **Plotly**
- **Library**: https://plotly.com
- **License**: MIT
- Interactive chart generation

### **Flask**
- **Library**: https://flask.palletsprojects.com
- **License**: BSD-3-Clause
- Web application framework

---

## 📜 License Compliance

This application is released under the **MIT License**, which is compatible with all the models and libraries used.

All models are used in accordance with their respective licenses:
- ✅ **Commercial use allowed** (all models)
- ✅ **Modification allowed** (all models)
- ✅ **Distribution allowed** (with proper attribution)
- ✅ **Private use allowed** (all models)

---

## 🌟 Thank You

Special thanks to:
- **HuggingFace** for hosting models and providing the Transformers library
- **University of Hong Kong** for FinBERT
- **Cardiff University** for Twitter-RoBERTa
- **Google Research** for BERT and DistilBERT
- **Open source community** for all supporting libraries

---

## 📝 How to Cite This Application

If you use this application in academic research, please cite it as:

```
@software{stockanalysishelper2025,
  title={AI Stock Portfolio Analyzer},
  author={Your Name/Organization},
  year={2025},
  url={https://github.com/JewelIT/StockAnalysisHelper}
}
```

And please cite the underlying models using the citations provided above.

---

## 🔗 Related Resources

- [HuggingFace Model Hub](https://huggingface.co/models)
- [FinBERT Documentation](https://huggingface.co/ProsusAI/finbert)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [Financial NLP Resources](https://github.com/topics/financial-nlp)

---

**Last Updated**: October 2025

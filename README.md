# 大溪桌球場域施工紀錄儀表板

大溪區綜合市民活動中心 4 樓桌球場域及多功能教室設置計畫的施工紀錄儀表板。
上傳施工日誌與照片後，GitHub 會自動重建並發布網頁。

## 一、第一次設定（只做一次）

1. 在 GitHub 建立新的 repository（公開），把這個資料夾裡**所有檔案**上傳，包含隱藏的 `.github` 資料夾。
   - 用網頁拖曳上傳時，Mac 的 Finder 預設看不到 `.github`。可以改用 GitHub Desktop 上傳，
     或在 GitHub 網頁按「Add file → Create new file」，檔名輸入 `.github/workflows/build.yml`，
     再把該檔內容貼上。
2. 到 repo 的 **Settings → Pages**，在「Build and deployment → Source」選 **GitHub Actions**。
3. 到 **Actions** 分頁，點「產生並發布儀表板」→「Run workflow」執行一次。
4. 完成後網址會是 `https://<你的帳號>.github.io/<repo 名稱>/`。

## 二、每天更新

| 要更新的東西 | 放在哪裡 | 說明 |
|---|---|---|
| 施工日誌 | `data/` | 上傳新的 .xls。**檔名開頭用日期**（例如 `2026_10_05_大溪施工日誌.xls`），系統會自動使用檔名排序最後的那份。舊檔可以刪除，也可以保留。 |
| 施工照片 | `photos/115-10-05/` | 每天一個資料夾，資料夾名稱就是拍照日期。可寫成 `115-10-05`、`2026-10-05` 或 `20261005`。 |
| 照片說明（可不填） | `photos/captions.csv` | 每張照片一列：資料夾、檔名、工項、說明。沒填的照片會顯示「現場」和檔名。 |

上傳後約 1–2 分鐘網頁就會更新。在 Actions 分頁可以看到每次執行結果；出現紅色叉叉代表失敗，點進去可以看錯誤訊息。

## 三、注意事項

- 網站是公開的，任何拿到網址的人都看得到契約金額與照片。照片請避免拍到人員正臉。
- 施工日誌必須維持目前的工作表結構（施工日誌、數量表、進度儲存區、總表）。如果範本改版導致失敗，請把錯誤訊息和新檔案交給 Claude 調整 `scripts/build.py`。
- 實際進度＝數量表的累計完成金額 ÷ 契約總價；預定進度取自「進度儲存區」。

## 四、檔案結構

```
data/                    施工日誌 .xls
photos/                  每日照片資料夾＋captions.csv
scripts/build.py         產生網頁的程式
scripts/template.html    網頁版面
.github/workflows/       GitHub 自動化流程
```

在自己電腦上預覽：`pip install -r requirements.txt` 後執行 `python scripts/build.py`，打開 `site/index.html`。

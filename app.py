from flask import Flask, render_template, jsonify
import speech_recognition as sr
import threading
import time

app = Flask(__name__)

#参照のみ → global は不要
#値の変更や再代入 → global が必要
# Recognizer と Microphone をグローバルに定義
r = sr.Recognizer()
m = sr.Microphone()

class MyThread(threading.Thread):
    def __init__(self, name, recognizer, microphone):
        super().__init__(name=name)  # threading.Threadの初期化を実行
        self.should_stop = False
        self.r = recognizer
        self.m = microphone
        self.is_first_time = True

    def run(self):
        while not self.should_stop:
            with self.m:
                print('準備完了。話してください。')
                audio = self.r.listen(m)
            
            try:
                result_text = self.r.recognize_google(audio, language='ja')
                print(f'Google Speech Recognition thinks you said {result_text}')
                
            except sr.WaitTimeoutError:
                print("タイムアウトしました。")
            except sr.UnknownValueError:
                print("音声を認識できませんでした。")
            except sr.RequestError as e:
                print("ネットワークエラーが発生しました。")
                
    def stop(self):
        self.should_stop = True

@app.route('/')
def index():
    # ノイズ音測定を1回だけ実施
    with m:
        r.adjust_for_ambient_noise(m)
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_recognition():
    global thread
    thread = MyThread("my_thread", r, m)
    thread.start()
    return '音声認識を開始しました。'

@app.route('/stop', methods=['POST'])
def stop_recognition():
    thread.stop()
    thread.join()
    return '音声認識を停止しました。'

if __name__ == '__main__':
    app.run(debug=True)
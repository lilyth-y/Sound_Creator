document.addEventListener('DOMContentLoaded', () => {
    const apiBaseUrl = window.location.origin;

    // Element Caching
    const voiceSelectA = document.getElementById('a-voice');
    const voiceSelectB = document.getElementById('b-voice');
    const generateBtn = document.getElementById('generate-btn');
    const resultSection = document.getElementById('result-section');
    const audioPlayer = document.getElementById('audio-player');
    const loadingSpinner = document.getElementById('loading-spinner');

    // --- 1. 페이지 로드 시 목소리 목록 가져오기 ---
    async function populateVoices() {
        try {
            const response = await fetch(`${apiBaseUrl}/api/voices`);
            if (!response.ok) throw new Error('목소리 목록을 가져오는 데 실패했습니다.');
            const { voices } = await response.json();

            voiceSelectA.innerHTML = '';
            voiceSelectB.innerHTML = '';
            for (const v of voices) {
                const optionA = new Option(v.label, v.id);
                const optionB = new Option(v.label, v.id);
                voiceSelectA.add(optionA);
                voiceSelectB.add(optionB);
            }
            // 기본값 설정 (존재하지 않을 수 있으니 첫 번째 값으로 fallback)
            voiceSelectA.value = voices[0]?.id || '';
            voiceSelectB.value = voices[1]?.id || voices[0]?.id || '';

        } catch (error) {
            console.error(error);
            alert(error.message);
        }
    }

    // 방언 사용 체크박스와 select 연동
    const useDialectCheckbox = document.getElementById('use-dialect');
    const dialectSelect = document.getElementById('dialect-select');
    useDialectCheckbox.addEventListener('change', () => {
        dialectSelect.disabled = !useDialectCheckbox.checked;
    });

    // --- ElevenLabs 목소리 목록 동적 로딩 ---
    const bTtsGcp = document.getElementById('b-tts-gcp');
    const bTtsElevenlabs = document.getElementById('b-tts-elevenlabs');
    const bElevenlabsVoiceGroup = document.getElementById('b-elevenlabs-voice-group');
    const bElevenlabsVoiceSelect = document.getElementById('b-elevenlabs-voice');
    let elevenlabsVoices = [];

    async function populateElevenlabsVoices() {
        try {
            const res = await fetch(`${apiBaseUrl}/api/elevenlabs-voices`);
            if (!res.ok) throw new Error('ElevenLabs 목소리 목록을 불러오지 못했습니다.');
            elevenlabsVoices = await res.json();
            bElevenlabsVoiceSelect.innerHTML = '';
            elevenlabsVoices.forEach(v => {
                const opt = new Option(`${v.name} (${v.description})`, v.voice_id);
                bElevenlabsVoiceSelect.add(opt);
            });
        } catch (e) {
            bElevenlabsVoiceSelect.innerHTML = '<option>불러오기 실패</option>';
        }
    }

    // TTS 엔진 선택에 따라 UI 토글
    function updateTtsEngineUI() {
        if (bTtsElevenlabs.checked) {
            bElevenlabsVoiceGroup.classList.add('active');
            populateElevenlabsVoices();
        } else {
            bElevenlabsVoiceGroup.classList.remove('active');
        }
    }
    bTtsGcp.addEventListener('change', updateTtsEngineUI);
    bTtsElevenlabs.addEventListener('change', updateTtsEngineUI);

    // AI 자동 목소리 선택에 따른 UI 토글
    const aiVoiceSelection = document.getElementById('ai-voice-selection');
    const bTtsEngineGroup = document.querySelector('fieldset');

    function updateAiVoiceSelectionUI() {
        const isAiSelected = aiVoiceSelection.checked;
        
        // 목소리 선택 UI 비활성화/활성화
        voiceSelectA.disabled = isAiSelected;
        voiceSelectB.disabled = isAiSelected;
        bElevenlabsVoiceSelect.disabled = isAiSelected;
        
        // TTS 엔진 선택 UI 비활성화/활성화
        bTtsGcp.disabled = isAiSelected;
        bTtsElevenlabs.disabled = isAiSelected;
        
        // 시각적 피드백
        if (isAiSelected) {
            voiceSelectA.style.opacity = '0.5';
            voiceSelectB.style.opacity = '0.5';
            bElevenlabsVoiceSelect.style.opacity = '0.5';
            bTtsEngineGroup.style.opacity = '0.5';
        } else {
            voiceSelectA.style.opacity = '1';
            voiceSelectB.style.opacity = '1';
            bElevenlabsVoiceSelect.style.opacity = '1';
            bTtsEngineGroup.style.opacity = '1';
        }
    }
    
    aiVoiceSelection.addEventListener('change', updateAiVoiceSelectionUI);

    // --- 2. 생성 버튼 클릭 이벤트 리스너 ---
    generateBtn.addEventListener('click', async (event) => {
        event.preventDefault(); // 폼 submit 방지
        // --- UI 업데이트: 로딩 시작 ---
        setLoading(true);

        // --- 입력 데이터 수집 ---
        const date = document.getElementById('date').value;
        const useDialect = useDialectCheckbox.checked;
        const dialect = useDialect ? dialectSelect.value : null;
        const relationship = document.getElementById('relationship').value; // 관계 필드 별도 변수로 추출
        const duration = parseInt(document.getElementById('duration').value, 10) || 30; // 지속 시간 추가
        
        // AI 자동 목소리 선택 옵션 확인
        const useAiVoiceSelection = document.getElementById('ai-voice-selection')?.checked || false;
        
        // --- 화자 B TTS 엔진 분기 ---
        const bTtsEngine = bTtsElevenlabs.checked ? 'elevenlabs' : 'gcp';
        let audioUrl = null;
        let requestData = {
            speaker_a: {
                gender: document.getElementById('a-gender').value,
                age: document.getElementById('a-age').value,
                personality: document.getElementById('a-personality').value,
                voice_id: useAiVoiceSelection ? null : voiceSelectA.value, // AI 선택 시 null
                tts_engine: useAiVoiceSelection ? null : 'gcp'  // AI 선택 시 null
            },
            speaker_b: {
                gender: document.getElementById('b-gender').value,
                age: document.getElementById('b-age').value,
                personality: document.getElementById('b-personality').value,
                voice_id: useAiVoiceSelection ? null : (bTtsEngine === 'elevenlabs' ? bElevenlabsVoiceSelect.value : voiceSelectB.value), // AI 선택 시 null
                tts_engine: useAiVoiceSelection ? null : bTtsEngine  // AI 선택 시 null
            },
            relationship: relationship, // 반드시 포함
            tags: document.getElementById('tags').value.split(',').map(tag => tag.trim()),
            date: date,
            dialect: dialect,
            duration_seconds: duration,
            use_ai_voice_selection: useAiVoiceSelection, // AI 자동 선택 플래그
        };
        console.log('requestData:', requestData); // 실제 전송 데이터 확인
        try {
            // 모든 경우에 실제 대화 생성 API 호출 (AI 자동 선택 포함)
            const response = await fetch(`${apiBaseUrl}/api/generate-audio/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || JSON.stringify(errorData) || '오디오 생성에 실패했습니다.');
            }
            const audioBlob = await response.blob();
            audioUrl = URL.createObjectURL(audioBlob);
            
            // --- UI 업데이트: 결과 표시 ---
            audioPlayer.src = audioUrl;
            resultSection.classList.remove('hidden');

        } catch (error) {
            console.error(error);
            alert(`오류가 발생했습니다: ${error.message}`);
        } finally {
            // --- UI 업데이트: 로딩 종료 ---
            setLoading(false);
        }
    });

    // --- 로딩 상태 관리 함수 ---
    function setLoading(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            loadingSpinner.classList.remove('hidden');
            resultSection.classList.add('hidden');
        } else {
            generateBtn.disabled = false;
            loadingSpinner.classList.add('hidden');
        }
    }

    // --- 초기화 실행 ---
    populateVoices();
});
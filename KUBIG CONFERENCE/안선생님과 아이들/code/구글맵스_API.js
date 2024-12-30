function getFastestRoutes() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('경로'); // "경로"라는 이름의 시트 가정
    const lastRow = sheet.getLastRow(); // 스프레드시트에 입력된 마지막 행
    const apiKey = 'apikeyhere'; // Google API Key 입력
    
    const departureTime = new Date();
    departureTime.setHours(13, 0, 0, 0); // 오후 1시로 시간 설정
  
    for (let row = 2; row <= lastRow; row++) {
      const origin = sheet.getRange(row, 1).getValue(); // A열: 출발지
      const la = sheet.getRange(row, 3).getValue(); // B열: 목적지
      const lo = sheet.getRange(row, 4).getValue(); // C열: 목적지
      const destination = `${la},${lo}`
      
      if (origin && destination) {
        const request = {
          origin: encodeURIComponent(origin),
          destination: encodeURIComponent(destination),
          travelMode: 'transit',
          transitOptions: {
            departureTime: departureTime, // 현재 시간 기준
            modes: ['BUS', 'SUBWAY'],  // 버스와 지하철만 사용
            routingPreference: 'FEWER_TRANSFERS' // 환승 적게 설정
          },
          // unitSystem: 'metric' // 미터법 사용
        };
  
        const url = buildDirectionsUrl(request, apiKey);
        const response = UrlFetchApp.fetch(url);
        const data = JSON.parse(response.getContentText());
  
        if (data.status === 'OK') {
          const bestRoute = getBestRoute(data.routes);
          writeRouteDetailsToSheet(sheet, bestRoute, row);  // 가장 짧은 경로를 출력하는 함수
        } else {
          Logger.log('Directions request failed due to ' + data.status);
          sheet.getRange(row, 5).setValue('Error: ' + data.status); // 에러 표시
        }
      }
    }
  }
  
  // URL 생성 함수
  function buildDirectionsUrl(request, apiKey) {
    const baseUrl = 'https://maps.googleapis.com/maps/api/directions/json?';
    
    const params = {
      origin: request.origin,
      destination: request.destination,
      mode: request.travelMode.toLowerCase(),
      transit_mode: request.transitOptions.modes.join('%7C').toLowerCase(),  // '|' 대신 '%7C' 사용
      transit_routing_preference: request.transitOptions.routingPreference.toLowerCase(),
      departure_time: Math.floor(request.transitOptions.departureTime.getTime() / 1000),
      // units: request.unitSystem === 'metric' ? 'metric' : 'imperial',
      key: apiKey
    };
  
    const query = Object.entries(params)
      .map(([key, value]) => `${key}=${value}`)
      .join('&');
    
    return `${baseUrl}${query}`;
  }
  
  // 가장 짧은 경로 선택 함수
  function getBestRoute(routes) {
    return routes.reduce((bestRoute, currentRoute) => {
      return currentRoute.legs[0].duration.value < bestRoute.legs[0].duration.value ? currentRoute : bestRoute;
    });
  }
  
  // 경로 세부 정보 스프레드시트에 작성 함수
  function writeRouteDetailsToSheet(sheet, route, row) {
    const leg = route.legs[0];  // 각 경로의 첫 번째 leg만 사용 (대부분은 하나의 leg만 있음)
    const totalDuration = leg.duration.text; // 총 소요 시간
    const totalDistance = leg.distance.text
    
    let transportDetails = '';  // 이동 수단 및 소요 시간 문자열
    let stepCol = 7;  // 이동수단 정보는 D열부터 시작
  
    leg.steps.forEach(step => {
      const stepMode = step.travel_mode;  // WALKING, TRANSIT 등
      const stepDuration = step.duration.text;  // 이 단계의 소요 시간
      const stepInstruction = step.html_instructions.replace(/<[^>]*>?/gm, ''); // 지시 사항에서 HTML 제거
  
      if (stepMode === 'TRANSIT' && step.transit_details) {
        const line = step.transit_details.line.short_name;  // 노선 이름 (버스 번호 등)
        const vehicleType = step.transit_details.line.vehicle.type;  // 교통수단 유형 (버스, 지하철 등)
        transportDetails = `${vehicleType} (${line}): ${stepDuration}`;
      } else {
        transportDetails = `${stepMode}: ${stepDuration}`;
      }
  
      // 각 단계를 스프레드시트에 출력
      sheet.getRange(row, stepCol).setValue(transportDetails);
      stepCol++;  // 다음 열로 이동
    });
  
    // 총 소요 시간을 C열에 출력
    sheet.getRange(row, 5).setValue(`총 이동거리: ${totalDistance}`);
    sheet.getRange(row, 6).setValue(`총 소요 시간: ${totalDuration}`);
  }
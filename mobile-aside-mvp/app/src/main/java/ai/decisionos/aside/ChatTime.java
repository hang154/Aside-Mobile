package ai.decisionos.aside;
import java.time.*;import java.util.regex.*;
/** Deterministic interpretation of user-supplied Korean dates; no model-generated timestamps. */
final class ChatTime {
 static final ZoneId SEOUL=ZoneId.of("Asia/Seoul");
 static long parse(String text,long now){
  ZonedDateTime clock=Instant.ofEpochMilli(now).atZone(SEOUL);
  Matcher m=Pattern.compile("(\\d{4}-\\d{2}-\\d{2})[T ](\\d{2}:\\d{2}(?::\\d{2}(?:\\.\\d{1,9})?)?)(Z|[+-]\\d{2}:?\\d{2})?").matcher(text);
  if(m.find()){
   String local=m.group(1)+"T"+m.group(2),offset=m.group(3);
   if(offset!=null){if(offset.matches("[+-][0-9]{4}"))offset=offset.substring(0,3)+":"+offset.substring(3);return OffsetDateTime.parse(local+offset).toInstant().toEpochMilli();}
   return LocalDateTime.parse(local).atZone(SEOUL).toInstant().toEpochMilli();
  }
  m=Pattern.compile("(\\d+)\\s*(분|시간|초)\\s*(후|뒤)").matcher(text);
  if(m.find()){long n=Long.parseLong(m.group(1)),unit=m.group(2).equals("시간")?3600000:m.group(2).equals("분")?60000:1000;return Math.addExact(now,Math.multiplyExact(n,unit));}
  LocalDate day=clock.toLocalDate();boolean explicit=false;
  m=Pattern.compile("(?:(\\d{4})년\\s*)?(\\d{1,2})월\\s*(\\d{1,2})일").matcher(text);
  if(m.find()){day=LocalDate.of(m.group(1)==null?day.getYear():Integer.parseInt(m.group(1)),Integer.parseInt(m.group(2)),Integer.parseInt(m.group(3)));explicit=true;}
  else if(text.contains("모레")){day=day.plusDays(2);explicit=true;}else if(text.contains("내일")){day=day.plusDays(1);explicit=true;}else if(text.contains("오늘")){explicit=true;}
  else {m=Pattern.compile("(다음\\s*주\\s*)?([월화수목금토일])요일").matcher(text);if(m.find()){int target="월화수목금토일".indexOf(m.group(2))+1;int delta=(target-day.getDayOfWeek().getValue()+7)%7;if(m.group(1)!=null)delta=target-day.getDayOfWeek().getValue()+7;day=day.plusDays(delta);explicit=true;}}
  m=Pattern.compile("(?:(오전|오후|아침|저녁|밤)\\s*)?(\\d{1,2})(?::(\\d{2})|시(?:\\s*(반|\\d{1,2}분))?)").matcher(text);
  if(!m.find())return 0;
  int hour=Integer.parseInt(m.group(2)),minute=m.group(3)!=null?Integer.parseInt(m.group(3)):m.group(4)==null?0:m.group(4).equals("반")?30:Integer.parseInt(m.group(4).replace("분",""));String period=m.group(1);
  if(period!=null){if(hour<1||hour>12)throw new IllegalArgumentException("12-hour clock");boolean midnight=period.equals("밤")&&hour==12;hour%=12;if(period.equals("오후")||period.equals("저녁")||(period.equals("밤")&&!midnight))hour+=12;if(midnight)day=day.plusDays(1);}
  long due=day.atTime(hour,minute).atZone(SEOUL).toInstant().toEpochMilli();if(!explicit&&due<=now)due=day.plusDays(1).atTime(hour,minute).atZone(SEOUL).toInstant().toEpochMilli();return due;
 }
 static String repeat(String text){if(text.contains("매일")||text.contains("날마다"))return "daily";if(text.contains("평일마다")||text.contains("매 평일"))return "weekdays";if(text.contains("매주"))return "weekly";return "";}
 static long next(long previous,String repeat,long now){ZonedDateTime date=Instant.ofEpochMilli(previous).atZone(SEOUL);do{date=date.plusDays(repeat.equals("weekly")?7:1);}while(date.toInstant().toEpochMilli()<=now||(repeat.equals("weekdays")&&date.getDayOfWeek().getValue()>5));return date.toInstant().toEpochMilli();}
}

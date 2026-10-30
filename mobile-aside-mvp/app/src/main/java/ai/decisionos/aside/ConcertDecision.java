package ai.decisionos.aside;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.time.temporal.ChronoUnit;
import java.util.Locale;

/** Compares user-verified values; never fetches or invents timetables or prices. */
public final class ConcertDecision {
    private static final DateTimeFormatter FORMAT = DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm", Locale.ROOT).withResolverStyle(ResolverStyle.STRICT);
    public static String calculate(String end, String exit, String travel, String train, String people, String budget, String todayFare, String hotel, String nextFare) {
        try {
            LocalDateTime ending=LocalDateTime.parse(end.trim(),FORMAT), departure=LocalDateTime.parse(train.trim(),FORMAT);
            long e=num(exit,1440), t=num(travel,1440), n=num(people,1000), b=num(budget,1000000000L), fare=num(todayFare,1000000000L), h=num(hotel,1000000000L), next=num(nextFare,1000000000L);
            if(n==0) throw new IllegalArgumentException();
            LocalDateTime arrival=ending.plusMinutes(e+t);
            long margin=ChronoUnit.MINUTES.between(arrival,departure);
            long today=Math.multiplyExact(fare,n), overnight=Math.addExact(h,Math.multiplyExact(next,n));
            String result="역 도착 예상: "+FORMAT.format(arrival)+"\n";
            if(departure.isBefore(ending)) result+="열차가 공연 종료 전 출발합니다. 날짜와 시간을 확인하세요.\n";
            else if(margin<0) result+="당일 열차: 예상 도착보다 "+(-margin)+"분 일찍 출발 · 탑승 어려움\n";
            else result+="당일 열차: 출발까지 "+margin+"분 여유 · 실제 운행과 탑승 가능 여부 확인\n";
            result+="당일 귀가 총액: "+today+"원"+(today<=b?" · 입력 예산 이내":" · 입력 예산 초과")+"\n";
            result+="숙박 후 귀가 총액: "+overnight+"원"+(overnight<=b?" · 입력 예산 이내":" · 입력 예산 초과")+"\n";
            result+="숙박 후 1인당: "+(overnight/n)+"원"+(overnight%n==0?"":" (나머지 "+(overnight%n)+"원)")+"\n";
            return result+"입력한 귀가비·숙박비만 계산했어요. 공연비·가는 교통비·식비는 제외됩니다. 예매·빈자리·가격은 직접 확인하세요.";
        } catch (Exception ex) { return "입력 오류: 날짜는 YYYY-MM-DD HH:mm, 인원은 1 이상, 시간·금액은 0 이상의 숫자로 입력하세요."; }
    }
    private static long num(String value,long max) { long n=Long.parseLong(value.trim()); if(n<0||n>max)throw new IllegalArgumentException(); return n; }
    private ConcertDecision() {}
}

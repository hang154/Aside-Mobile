import ai.decisionos.aside.ConcertDecision;
public class TestConcertDecision {
  static void has(String output,String expected){if(!output.contains(expected))throw new AssertionError(expected+" missing from "+output);}
  static String run(String end,String exit,String travel,String train,String people,String budget,String fare,String hotel,String next){return ConcertDecision.calculate(end,exit,travel,train,people,budget,fare,hotel,next);}
  public static void main(String[] args){
    String late=run("2026-11-14 22:30","30","40","2026-11-14 23:20","2","200000","30000","100000","30000");
    has(late,"2026-11-14 23:40");has(late,"20분 일찍");has(late,"당일 귀가 총액: 60000원");has(late,"숙박 후 귀가 총액: 160000원");
    String nextDay=run("2026-11-14 23:30","20","30","2026-11-15 00:30","3","100000","20000","40000","20000");
    has(nextDay,"2026-11-15 00:20");has(nextDay,"10분 여유");has(nextDay,"나머지 1원");
    has(run("2026-02-30 22:00","0","0","2026-03-01 00:00","1","1","1","1","1"),"입력 오류");
    has(run("2026-11-14 22:00","0","0","2026-11-14 23:00","0","1","1","1","1"),"입력 오류");
    has(run("2026-11-14 22:00","-1","0","2026-11-14 23:00","1","1","1","1","1"),"입력 오류");
    has(run("2026-11-14 22:00","0","0","2026-11-14 21:00","1","0","1","1","1"),"공연 종료 전");
    System.out.println("Concert scenario calculations: PASS (6 cases)");
  }
}

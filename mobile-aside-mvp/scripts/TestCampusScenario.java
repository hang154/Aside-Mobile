import ai.decisionos.aside.CampusScenario;
import java.util.HashSet;
public class TestCampusScenario {
 public static void main(String[] args){HashSet<String> names=new HashSet<>();int school=0, general=0;
  for(CampusScenario s:CampusScenario.ALL){if(!names.add(s.title))throw new AssertionError("duplicate: "+s.title);if(s.title.isEmpty()||s.description.isEmpty()||s.query.isEmpty())throw new AssertionError("missing text");if(s.requiresSchool){school++;if(!s.queryFor(" ").isEmpty())throw new AssertionError("school missing");if(!s.queryFor("예시대학교").startsWith("예시대학교 "))throw new AssertionError("wrong school query");}else{general++;if(s.queryFor("").isEmpty())throw new AssertionError("empty query");}}
  if(school<5||general<5)throw new AssertionError("missing scenarios");System.out.println("PASS campus scenarios: "+names.size()+" (school="+school+", general="+general+")");
 }
}

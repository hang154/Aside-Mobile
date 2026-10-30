import ai.decisionos.aside.ActionProposal;
public class TestActionProposal {
    private static int count;
    private static void check(String value, ActionProposal.Type type, String query){
        ActionProposal p=ActionProposal.parse(value);count++;
        if(p.type!=type||!p.query.equals(query))throw new AssertionError("unexpected: "+value);
    }
    public static void main(String[] args){
        check("NAVER",ActionProposal.Type.NAVER,"");
        check(" SEARCH|서울 공연 근처 숙소 ",ActionProposal.Type.SEARCH,"서울 공연 근처 숙소");
        check("SEARCH|2026-11-20 KTX",ActionProposal.Type.SEARCH,"2026-11-20 KTX");
        check(null,ActionProposal.Type.NONE,"");
        check("",ActionProposal.Type.NONE,"");
        check("NAVER\nSEARCH|x",ActionProposal.Type.NONE,"");
        check("SEARCH|hello\nNAVER",ActionProposal.Type.NONE,"");
        check("SEARCH|https://example.com",ActionProposal.Type.NONE,"");
        check("SEARCH|tel:112",ActionProposal.Type.NONE,"");
        check("SEARCH|x; rm -rf",ActionProposal.Type.NONE,"");
        check("SEARCH|",ActionProposal.Type.NONE,"");
        check("SEARCH|"+"x".repeat(121),ActionProposal.Type.NONE,"");
        check("OPEN|TOSS",ActionProposal.Type.NONE,"");
        System.out.println("PASS "+count+" action proposal cases");
    }
}

package ai.decisionos.aside;

import java.util.regex.Pattern;

/** Only explicit search or fixed website proposals. No URLs, intent schemes, or free-form commands. */
public final class ActionProposal {
    public enum Type { SEARCH, NAVER, NONE }
    public final Type type;
    public final String query;
    private ActionProposal(Type type,String query){this.type=type;this.query=query;}
    private static final Pattern SAFE=Pattern.compile("[\\p{L}\\p{N} \\t.,!?()·~_-]{1,120}");
    public static ActionProposal parse(String raw){
        if(raw==null)return new ActionProposal(Type.NONE,"");
        String s=raw.trim();
        if(s.equals("NAVER"))return new ActionProposal(Type.NAVER,"");
        if(s.startsWith("SEARCH|")){
            String q=s.substring(7).trim();
            if(SAFE.matcher(q).matches())return new ActionProposal(Type.SEARCH,q);
        }
        return new ActionProposal(Type.NONE,"");
    }
}
